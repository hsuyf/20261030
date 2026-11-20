# AI 小幫手啟用設定

浮動對話框已接到 Firebase AI Logic。要讓 Gemini 回覆，請在 Firebase 專案 `project-2711674805927151385` 完成以下設定：

1. 在專案目錄執行 `npx -y firebase-tools@latest projects:list`，確認目前專案是 `project-2711674805927151385`。
2. 執行 `npx -y firebase-tools@latest init ailogic`，選擇 Gemini Developer API 以啟用 Firebase AI Logic。
3. 在 Google Cloud 專案 `project-2711674805927151385` 建立 reCAPTCHA Enterprise Web score-based key，允許網域 `hsuyf.github.io`。正式使用的 key 不要加入 `localhost`。
4. 在 Firebase Console 的 **App Check > Apps** 使用同一個 key 註冊這個 Web app，並在 **APIs** 中確認 Firebase AI Logic 使用 App Check 保護。
5. 將 reCAPTCHA Enterprise **網站金鑰**填入 `firebase-config.js` 的 `appCheckRecaptchaSiteKey`。CLI 顯示的 `firebase-config.json` 是設定參考；這個專案實際載入的是 `firebase-config.js`，不需要另外建立 JSON 檔。
6. 將變更部署至 GitHub Pages，並從 `https://hsuyf.github.io/20261030/` 登入後使用。

網站金鑰是瀏覽器端設定值；不要把 reCAPTCHA 的密鑰或任何 App Check debug token 放進這個檔案。小幫手會把目前帳號的行程資料與最近對話送至 Gemini 產生回答，不會把對話寫入 Firestore。
