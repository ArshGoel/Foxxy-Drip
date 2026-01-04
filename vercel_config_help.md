# Vercel Payload Error Fix

## Changes Made:

### 1. Updated `vercel.json`
- **Increased `maxLambdaSize`** from 15MB to 50MB (maximum allowed)
- **Added `maxDuration`** set to 60 seconds for function timeout
- **Added environment variables** for upload size limits

### 2. Updated `settings.py`
- **Increased `DATA_UPLOAD_MAX_MEMORY_SIZE`** to 100MB
- **Increased `FILE_UPLOAD_MAX_MEMORY_SIZE`** to 100MB
- **Added `DATA_UPLOAD_MAX_NUMBER_FIELDS`** to support multiple file uploads
- **Added `FILE_UPLOAD_PERMISSIONS`** for proper file handling

### 3. How Cloudinary Helps
You're already using **Cloudinary as your storage backend** (configured in settings.py):
```python
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```
This means images are uploaded **directly to Cloudinary**, not stored on Vercel's file system. This bypasses Vercel's payload limits entirely!

## Best Practices for Image Uploads on Vercel:

1. **Compress images before uploading** - Use image optimization libraries
2. **Upload one image at a time** instead of batches if issues persist
3. **Ensure Cloudinary credentials** are set in environment variables:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

## If Still Getting Errors:

1. Check browser console for exact error message
2. Verify Cloudinary API credentials are correct
3. Check Cloudinary account for upload limits (free tier: 25MB per file)
4. Consider uploading one image at a time with client-side batching

## Testing:
After deploying these changes to Vercel, try uploading product images again.
