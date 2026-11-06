// Firebase Google Authentication for the GitHub Pages site.
// The public Firebase web config is not a secret. Enable Google sign-in in Firebase
// Console and add hsuyf.github.io to Authentication > Settings > Authorized domains.
import { initializeApp } from 'https://www.gstatic.com/firebasejs/12.4.0/firebase-app.js';
import {
  getAuth,
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithRedirect,
  signOut,
  getRedirectResult
} from 'https://www.gstatic.com/firebasejs/12.4.0/firebase-auth.js';
import { firebaseConfig } from './firebase-config.js';

const { authDomainOverride, ...appConfig } = firebaseConfig;
const app = initializeApp(appConfig);
const auth = getAuth(app);
if (authDomainOverride) auth.config.authDomain = authDomainOverride;
const provider = new GoogleAuthProvider();
// GitHub Pages uses a shared hsuyf.github.io origin; redirect-based OAuth
// returns to this project path without relying on a popup opener.
const authScreen = document.getElementById('authScreen');
const appRoot = document.getElementById('appRoot');
const signInButton = document.getElementById('googleSignIn');
const signOutButton = document.getElementById('signOut');
const authError = document.getElementById('authError');
const authLoading = document.getElementById('authLoading');
const profileInfo = document.getElementById('profileInfo');
const profileAvatar = document.getElementById('profileAvatar');

function showError(error) {
  const messages = {
    'auth/unauthorized-domain': '此網站網域尚未加入 Firebase 授權網域，請在 Firebase Authentication 設定中加入 hsuyf.github.io。',
    'auth/popup-closed-by-user': '登入視窗已關閉，請再次嘗試。',
    'auth/popup-blocked': '瀏覽器封鎖了登入視窗，請允許此網站開啟彈出視窗後重試。',
    'auth/network-request-failed': '網路連線失敗，請檢查網路後重試。'
  };
  authError.textContent = messages[error?.code] || '登入未完成，請稍後重試。';
  console.error('Firebase authentication error:', error);
}

onAuthStateChanged(auth, (user) => {
  authLoading.hidden = true;
  authScreen.hidden = Boolean(user);
  appRoot.hidden = !user;
  if (user) {
    profileInfo.replaceChildren(document.createTextNode(user.displayName || '已登入'));
    const email = document.createElement('small');
    email.textContent = user.email || '';
    profileInfo.append(email);
    profileAvatar.textContent = (user.displayName || user.email || '日').slice(0, 1);
    profileAvatar.style.backgroundImage = user.photoURL ? `url("${user.photoURL}")` : '';
    profileAvatar.style.backgroundSize = 'cover';
    profileAvatar.style.backgroundPosition = 'center';
  } else {
    profileInfo.textContent = '已登入';
    profileAvatar.textContent = '日';
  }
});

authLoading.hidden = false;
getRedirectResult(auth).catch((error) => {
  if (error) showError(error);
});
signInButton.addEventListener('click', async () => {
  authError.textContent = '';
  signInButton.disabled = true;
  try {
    await signInWithRedirect(auth, provider);
  } catch (error) {
    showError(error);
  } finally {
    signInButton.disabled = false;
  }
});

signOutButton.addEventListener('click', async () => {
  try {
    await signOut(auth);
  } catch (error) {
    showError(error);
  }
});
