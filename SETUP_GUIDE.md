# 🚀 Complete Setup Guide — GitHub + Railway.app (FREE)

---

## STEP 1: GitHub Par Account Banao

1. Browser mein jao: **https://github.com**
2. "Sign up" click karo
3. Email, password, username dalo
4. Email verify karo

---

## STEP 2: New Repository Banao

1. GitHub mein login ke baad: **https://github.com/new**
2. Repository name: `video-scraper`
3. "Public" select karo
4. "Create repository" click karo

---

## STEP 3: Files Upload Karo (Drag & Drop)

1. ZIP file apne PC par **Extract/Unzip** karo
   - Windows: Right click → "Extract All"
   - Extracted folder ka naam: `scraper`

2. GitHub par apni repo open karo
3. "uploading an existing file" link click karo
4. Extracted `scraper` folder ke **andar** jao
5. **Saari files select karo** (Ctrl+A) aur GitHub page par **drag & drop** karo
6. Neeche "Commit changes" green button click karo

✅ Files GitHub par upload ho gayi!

---

## STEP 4: Railway.app Par Deploy Karo

1. Browser mein jao: **https://railway.app**
2. "Login" → "Login with GitHub" click karo
3. GitHub account allow karo

4. Dashboard mein: **"New Project"** click karo
5. **"Deploy from GitHub repo"** select karo
6. `video-scraper` repo select karo
7. Railway automatically build shuru karega

⏳ 3-5 minute wait karo — build ho raha hai

---

## STEP 5: URL Lao

1. Railway dashboard mein apna project open karo
2. **"Settings"** tab click karo
3. **"Domains"** section mein jao
4. **"Generate Domain"** click karo
5. Tumhe milega kuch aisa:
   ```
   https://video-scraper-production-abc123.up.railway.app
   ```
6. Yeh URL copy karo ✂️

---

## STEP 6: Test Karo

Browser mein yeh URL kholo:
```
https://YOUR-URL.up.railway.app/docs
```

Agar page khule toh ✅ **Kaam kar raha hai!**

---

## STEP 7: n8n Mein Lagao

Apne n8n mein "video details" node ki settings badlo:

### TikTok Download Node:
- **Method:** `POST`
- **URL:** `https://YOUR-URL.up.railway.app/api/video/download`
- **Body (JSON):**
```json
{
  "url": "{{ $json.TikTok_Link }}",
  "platform": "tiktok"
}
```

### TikTok Details Node:
- **Method:** `POST`
- **URL:** `https://YOUR-URL.up.railway.app/api/video/details`
- **Body (JSON):**
```json
{
  "url": "{{ $json.TikTok_Link }}"
}
```

---

## ✅ Tumhara Current n8n Flow Fix

Purana broken node:
```
GET https://api.azbry.com/api/download/tiktok?url=...
```

Naya working node:
```
POST https://YOUR-URL.up.railway.app/api/video/download
Body: { "url": "{{ $json.TikTok_Link }}", "platform": "tiktok" }
```

---

## ⚠️ Important Notes

- Railway free mein **500 hours/month** deta hai — kaafi hai
- Videos temporarily download hoti hain — Railway restart pe delete ho jati hain
- Isliye download ke baad **turant YouTube par upload** karo n8n se
- API docs hamesha yahan milenge: `https://YOUR-URL.up.railway.app/docs`

---

## Koi Masla Aaye Toh

Railway dashboard mein "Deployments" tab mein **logs** dekho — wahan error show hogi.
