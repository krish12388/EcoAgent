# 🔒 SECURITY NOTICE

## ⚠️ IMPORTANT: API Key Security

### If You Cloned This Repository Before February 17, 2026

**Your API key may have been exposed in an earlier commit.**

### What to do:

1. **Immediately regenerate your Groq API key**
   - Go to: https://console.groq.com/keys
   - Delete the old key
   - Create a new key

2. **Update your local `.env` file**
   - Copy `backend/.env.example` to `backend/.env`
   - Add your new API key to `backend/.env`

3. **Verify `.env` is in `.gitignore`**
   - The `.env` file should NEVER be committed to git
   - Check that `.gitignore` includes `.env`

### For New Users

1. Copy the example environment file:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Add your API key to `backend/.env`:
   ```env
   GROQ_API_KEY=your_new_api_key_here
   ```

3. **Never commit the `.env` file!**

### Repository History

The repository history was cleaned on [Current Date] to remove any sensitive files. All commits prior to this date were rewritten.

### Best Practices

- ✅ Always keep `.env` files in `.gitignore`
- ✅ Use `.env.example` for templates (without real keys)
- ✅ Rotate API keys regularly
- ✅ Use environment variables for all secrets
- ❌ Never hardcode API keys in source code
- ❌ Never commit `.env` files to version control

### Questions?

If you have security concerns, please open an issue or contact the repository owner.
