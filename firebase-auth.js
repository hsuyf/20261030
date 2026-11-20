// Firebase Authentication and per-user Firestore persistence for GitHub Pages.
import { initializeApp } from 'https://www.gstatic.com/firebasejs/12.4.0/firebase-app.js';
import {
  getAuth,
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  signOut
} from 'https://www.gstatic.com/firebasejs/12.4.0/firebase-auth.js';
import {
  collection,
  deleteDoc,
  doc,
  getDoc,
  getDocs,
  getFirestore,
  query,
  setDoc,
  where
} from 'https://www.gstatic.com/firebasejs/12.4.0/firebase-firestore.js';
import {
  initializeAppCheck,
  ReCaptchaEnterpriseProvider
} from 'https://www.gstatic.com/firebasejs/12.4.0/firebase-app-check.js';
import { initAiAssistant } from './ai-assistant.js';
import { firebaseConfig } from './firebase-config.js';

const app = initializeApp(firebaseConfig);
if (firebaseConfig.appCheckRecaptchaSiteKey) {
  initializeAppCheck(app, {
    provider: new ReCaptchaEnterpriseProvider(firebaseConfig.appCheckRecaptchaSiteKey),
    isTokenAutoRefreshEnabled: true
  });
}
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();
const authScreen = document.getElementById('authScreen');
const appRoot = document.getElementById('appRoot');
const signInButton = document.getElementById('googleSignIn');
const signOutButton = document.getElementById('signOut');
const authError = document.getElementById('authError');
const authLoading = document.getElementById('authLoading');
const profileInfo = document.getElementById('profileInfo');
const profileAvatar = document.getElementById('profileAvatar');
const cloudStatus = document.createElement('div');
cloudStatus.id = 'cloudSyncStatus';
cloudStatus.setAttribute('role', 'status');
cloudStatus.setAttribute('aria-live', 'polite');
cloudStatus.hidden = true;
cloudStatus.style.cssText = 'margin:0 0 18px;padding:10px 14px;border-radius:10px;font-size:12px;background:#fff2e6;color:#805a35';
document.querySelector('#appRoot .main')?.prepend(cloudStatus);

// Existing records use one document per tag/task/event/project. Project
// milestones are stored under each project to match firestore.rules.
let currentUser = null;
let authGeneration = 0;
let saveTimer = null;
let saveQueue = Promise.resolve();
let assistantInitialized = false;
const knownRecords = new Map();
const knownMilestones = new Map();

const recordsRef = (user) => collection(db, 'users', user.uid, 'records');
const recordRef = (user, recordId) => doc(db, 'users', user.uid, 'records', recordId);
const milestoneRef = (user, projectId, milestoneId) =>
  doc(db, 'users', user.uid, 'records', projectId, 'milestones', milestoneId);

function stableJson(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableJson).join(',')}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(',')}}`;
}

function attachId(item, id) {
  Object.defineProperty(item, '_firestoreId', {
    configurable: true,
    enumerable: false,
    writable: true,
    value: id
  });
  return item;
}

function recordData(kind, item, uid) {
  if (kind === 'tag') return { uid, kind, name: item.name, color: item.color };
  if (kind === 'task') return { uid, kind, name: item.name, date: item.date, tag: item.tag, done: Boolean(item.done) };
  if (kind === 'event') return { uid, kind, name: item.name, date: item.date, start: item.start, end: item.end, tag: item.tag };
  return {
    uid,
    kind: 'project',
    name: item.name,
    due: item.due,
    progress: Number(item.progress),
    next: item.next,
    done: Number(item.done)
  };
}

function setCloudStatus(message = '') {
  cloudStatus.textContent = message;
  cloudStatus.hidden = !message;
}

function showCloudError(error) {
  console.error('Firebase Firestore sync error:', error);
  setCloudStatus('雲端同步失敗；目前畫面仍可使用，但這次變更尚未保存。請檢查 Firestore 規則與網路後重新載入。');
}

function initializeAssistant() {
  if (assistantInitialized || !window.plannerStorage) return;
  initAiAssistant({
    app,
    getSchedule: () => window.plannerStorage.snapshot(),
    getUser: () => currentUser
  });
  assistantInitialized = true;
}

async function loadUserData(user) {
  const ownRecords = query(recordsRef(user), where('uid', '==', user.uid));
  const snapshot = await getDocs(ownRecords);
  const data = { tags: [], tasks: [], events: [], projects: [] };
  knownRecords.clear();
  knownMilestones.clear();

  for (const record of snapshot.docs) {
    const stored = record.data();
    knownRecords.set(record.id, stableJson(stored));
    if (stored.kind === 'tag') {
      data.tags.push(attachId({ name: stored.name, color: stored.color }, record.id));
    } else if (stored.kind === 'task') {
      data.tasks.push(attachId({ name: stored.name, date: stored.date, tag: stored.tag, done: stored.done }, record.id));
    } else if (stored.kind === 'event') {
      data.events.push(attachId({ name: stored.name, date: stored.date, start: stored.start, end: stored.end, tag: stored.tag }, record.id));
    } else if (stored.kind === 'project') {
      const milestonesQuery = query(
        collection(db, 'users', user.uid, 'records', record.id, 'milestones'),
        where('uid', '==', user.uid)
      );
      const milestonesSnapshot = await getDocs(milestonesQuery);
      const milestones = milestonesSnapshot.docs
        .map((milestone) => {
          knownMilestones.set(`${record.id}/${milestone.id}`, stableJson(milestone.data()));
          return milestone.data();
        })
        .sort((left, right) => left.order - right.order)
        .map((milestone) => milestone.name);
      data.projects.push(attachId({
        name: stored.name,
        due: stored.due,
        progress: stored.progress,
        next: stored.next,
        milestones,
        done: stored.done
      }, record.id));
    }
  }

  if (snapshot.empty) {
    // Keep the app's existing starter planner for a new account and save it
    // once, so later visits load that account's own copy from Firestore.
    await saveNow(user);
  } else {
    window.plannerStorage.replace(data);
  }
}

async function saveNow(user = currentUser) {
  if (!user || !window.plannerStorage) return;
  const state = window.plannerStorage.snapshot();
  const rows = [];
  const milestones = new Map();

  for (const [kind, items] of [['tag', state.tags], ['task', state.tasks], ['event', state.events], ['project', state.projects]]) {
    for (const item of items) {
      if (!item._firestoreId) attachId(item, doc(recordsRef(user)).id);
      const id = item._firestoreId;
      rows.push({ id, item, payload: recordData(kind, item, user.uid) });
      if (kind === 'project') {
        (item.milestones || []).forEach((name, order) => {
          const milestoneId = String(order);
          milestones.set(`${id}/${milestoneId}`, {
            projectId: id,
            milestoneId,
            payload: { uid: user.uid, name, order }
          });
        });
      }
    }
  }

  const currentIds = new Set(rows.map((row) => row.id));
  for (const [key] of knownMilestones) {
    if (milestones.has(key)) continue;
    const slash = key.lastIndexOf('/');
    const ref = milestoneRef(user, key.slice(0, slash), key.slice(slash + 1));
    const existing = await getDoc(ref);
    if (existing.exists()) await deleteDoc(ref);
    knownMilestones.delete(key);
  }

  // Save parents before adding milestones, because the rules require the
  // parent document to exist and have kind == "project".
  for (const row of rows) {
    const serialized = stableJson(row.payload);
    if (knownRecords.get(row.id) === serialized) continue;
    await setDoc(recordRef(user, row.id), row.payload);
    knownRecords.set(row.id, serialized);
  }

  for (const [key, milestone] of milestones) {
    const serialized = stableJson(milestone.payload);
    if (knownMilestones.get(key) === serialized) continue;
    await setDoc(milestoneRef(user, milestone.projectId, milestone.milestoneId), milestone.payload);
    knownMilestones.set(key, serialized);
  }

  for (const [id] of knownRecords) {
    if (currentIds.has(id)) continue;
    const ref = recordRef(user, id);
    const existing = await getDoc(ref);
    if (existing.exists()) await deleteDoc(ref);
    knownRecords.delete(id);
  }
  setCloudStatus('已同步至 Firebase');
  window.setTimeout(() => {
    if (cloudStatus.textContent === '已同步至 Firebase') setCloudStatus('');
  }, 1800);
}

function scheduleSave() {
  if (!currentUser) return;
  window.clearTimeout(saveTimer);
  saveTimer = window.setTimeout(() => {
    const user = currentUser;
    saveQueue = saveQueue.catch(() => {}).then(() => saveNow(user)).catch(showCloudError);
  }, 350);
}
window.firebaseScheduleSave = scheduleSave;

async function flushSave() {
  if (!currentUser) return;
  window.clearTimeout(saveTimer);
  const user = currentUser;
  saveQueue = saveQueue.catch(() => {}).then(() => saveNow(user));
  await saveQueue;
}

function showAuthError(error) {
  const messages = {
    'auth/unauthorized-domain': '此網站網域尚未加入 Firebase 授權網域，請在 Firebase Authentication 設定中加入 hsuyf.github.io。',
    'auth/popup-closed-by-user': '登入視窗已關閉，請再次嘗試。',
    'auth/cancelled-popup-request': '登入視窗已取消，請再次嘗試。',
    'auth/popup-blocked': '瀏覽器封鎖了登入視窗，請允許此網站開啟彈出視窗後重試。',
    'auth/network-request-failed': '網路連線失敗，請檢查網路後重試。'
  };
  authError.textContent = messages[error?.code] || '登入未完成，請稍後重試。';
  console.error('Firebase authentication error:', error);
}

signInButton.hidden = true;
authLoading.hidden = false;
onAuthStateChanged(auth, async (user) => {
  const generation = ++authGeneration;
  if (!user) {
    currentUser = null;
    window.resetAiAssistant?.();
    window.clearTimeout(saveTimer);
    authLoading.hidden = true;
    signInButton.hidden = false;
    authScreen.hidden = false;
    appRoot.hidden = true;
    setCloudStatus('');
    profileInfo.textContent = '已登入';
    profileAvatar.textContent = '日';
    return;
  }

  signInButton.hidden = true;
  authScreen.hidden = false;
  appRoot.hidden = true;
  authLoading.textContent = '正在載入雲端行程…';
  authLoading.hidden = false;
  profileInfo.replaceChildren(document.createTextNode(user.displayName || '已登入'));
  const email = document.createElement('small');
  email.textContent = user.email || '';
  profileInfo.append(email);
  profileAvatar.textContent = (user.displayName || user.email || '日').slice(0, 1);
  profileAvatar.style.backgroundImage = user.photoURL ? `url("${user.photoURL}")` : '';
  profileAvatar.style.backgroundSize = 'cover';
  profileAvatar.style.backgroundPosition = 'center';

  try {
    await loadUserData(user);
    if (generation !== authGeneration) return;
    currentUser = user;
    initializeAssistant();
    authLoading.hidden = true;
    authScreen.hidden = true;
    appRoot.hidden = false;
  } catch (error) {
    if (generation !== authGeneration) return;
    currentUser = user;
    initializeAssistant();
    authLoading.hidden = true;
    authError.textContent = '無法讀取 Firestore。請確認資料庫規則已部署，然後重新載入。';
    authScreen.hidden = true;
    appRoot.hidden = false;
    showCloudError(error);
  }
});

signInButton.addEventListener('click', async () => {
  authError.textContent = '';
  signInButton.disabled = true;
  try {
    await signInWithPopup(auth, provider);
  } catch (error) {
    showAuthError(error);
  } finally {
    signInButton.disabled = false;
  }
});

signOutButton.addEventListener('click', async () => {
  try {
    await flushSave();
    await signOut(auth);
  } catch (error) {
    showCloudError(error);
  }
});
