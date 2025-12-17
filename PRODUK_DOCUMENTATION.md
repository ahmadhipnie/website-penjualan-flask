# CRUD Produk dengan Multiple Upload - Dokumentasi

## 📝 Overview
Fitur CRUD lengkap untuk manajemen produk dengan kemampuan upload multiple gambar. Menggunakan halaman terpisah untuk tambah dan edit, serta preview gambar real-time.

## 🗂️ File Structure

```
├── model/
│   └── Produk.py                           # Model produk dengan image handling
├── controller/
│   └── admin/
│       └── ProdukController.py             # Controller CRUD produk
├── templates/
│   └── admin/
│       ├── produk/
│       │   ├── index.html                  # List produk
│       │   ├── tambah.html                 # Form tambah produk
│       │   └── edit.html                   # Form edit produk
│       └── layout/
│           └── sidebar_admin.html          # Menu produk
├── static/
│   └── gambar_produk/                      # Folder penyimpanan gambar
│       └── .gitkeep
└── main.py                                 # Blueprint registration
```

## 🎯 Fitur

### ✅ 1. Menampilkan Daftar Produk (Read)
- DataTables dengan pencarian & sorting
- Thumbnail gambar utama
- Nama produk + preview deskripsi
- Badge kategori
- Badge stok (hijau/kuning/merah)
- Format harga IDR
- Button Edit & Hapus

### ✅ 2. Tambah Produk (Create) - Halaman Terpisah
- Form lengkap: nama, kategori, deskripsi, harga, stok
- **Multiple file upload** (bisa upload banyak gambar sekaligus)
- Preview gambar sebelum upload
- Gambar pertama otomatis jadi gambar utama
- Validasi client-side & server-side
- Flash message konfirmasi

### ✅ 3. Edit Produk (Update) - Halaman Terpisah
- Form pre-filled dengan data existing
- **Tampil gambar existing** dengan thumbnail
- Set gambar mana yang jadi utama (badge "Utama")
- Hapus gambar individual dengan konfirmasi
- Upload gambar baru tambahan
- Preview gambar baru sebelum upload
- Informasi metadata (ID, created, updated)

### ✅ 4. Hapus Produk (Delete)
- SweetAlert2 konfirmasi
- Cascade delete: produk + semua gambarnya
- Delete file gambar dari storage
- AJAX request tanpa reload

### ✅ 5. Manajemen Gambar
- Upload multiple images
- Set primary image
- Delete individual image
- Auto-generate unique filename (UUID)
- Support format: PNG, JPG, JPEG, GIF, WEBP
- Validasi file extension
- Preview real-time

## 📋 Database Schema

### Tabel `barangs`
```sql
CREATE TABLE `barangs` (
  `id` bigint UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `id_kategori` bigint UNSIGNED NULL,
  `nama_barang` varchar(255) NOT NULL,
  `deskripsi` text NOT NULL,
  `harga` int NOT NULL,
  `stok` int NOT NULL,
  `created_at` timestamp NULL,
  `updated_at` timestamp NULL,
  FOREIGN KEY (id_kategori) REFERENCES kategoris(id)
);
```

### Tabel `gambar_barangs`
```sql
CREATE TABLE `gambar_barangs` (
  `id` bigint UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `id_barang` bigint UNSIGNED NOT NULL,
  `gambar_url` varchar(255) NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `created_at` timestamp NULL,
  `updated_at` timestamp NULL,
  FOREIGN KEY (id_barang) REFERENCES barangs(id) ON DELETE CASCADE
);
```

## 🔧 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/admin/produk` | List semua produk |
| GET | `/admin/produk/tambah` | Form tambah produk |
| POST | `/admin/produk/tambah` | Submit tambah produk |
| GET | `/admin/produk/edit/<id>` | Form edit produk |
| POST | `/admin/produk/edit/<id>` | Submit edit produk |
| POST | `/admin/produk/delete/<id>` | Hapus produk |
| POST | `/admin/produk/delete-image/<id>` | Hapus gambar |
| POST | `/admin/produk/set-primary/<produk_id>/<image_id>` | Set gambar utama |

## 💻 Cara Menggunakan

### 1. Tambah Produk Baru
```
1. Klik menu "Produk" di sidebar
2. Klik tombol "Tambah Produk"
3. Isi form:
   - Nama produk
   - Pilih kategori
   - Deskripsi lengkap
   - Harga (dalam Rupiah)
   - Stok tersedia
4. Klik "Pilih gambar" → pilih beberapa file sekaligus
5. Preview gambar akan muncul (gambar pertama = utama)
6. Klik "Simpan Produk"
7. Redirect ke list produk dengan pesan sukses
```

### 2. Edit Produk
```
1. Di list produk, klik tombol "Edit"
2. Form terbuka dengan data existing
3. Ubah data yang perlu diubah
4. Lihat gambar existing:
   - Badge "Utama" pada gambar primary
   - Klik "Set Utama" untuk ganti primary
   - Klik icon trash untuk hapus gambar
5. Upload gambar baru (opsional)
6. Klik "Update Produk"
```

### 3. Hapus Produk
```
1. Di list produk, klik tombol "Hapus"
2. Konfirmasi SweetAlert muncul
3. Klik "Ya, Hapus!"
4. Produk dan semua gambarnya terhapus
```

## 📁 Upload & Storage

### Konfigurasi Upload
```python
UPLOAD_FOLDER = 'static/gambar_produk'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
```

### Filename Generation
```python
# Generate unique filename dengan UUID
filename = f"{uuid.uuid4().hex}.{ext}"
# Contoh: a3f5c9d8e1b2f4a7c6d9e8b1a2c3d4e5.jpg
```

### File Validation
- Extension checking
- File existence check
- Auto-create directory if not exists

## 🎨 UI/UX Features

### List Produk
- **Thumbnail**: 60x60px, object-fit cover
- **Deskripsi**: Truncate 50 karakter + "..."
- **Harga**: Format IDR dengan separator
- **Stok Badge**: 
  - Hijau: > 10
  - Kuning: 1-10
  - Merah: 0 (Habis)

### Form Tambah
- Custom file input styling
- Multiple file selection indicator
- Preview grid 3 kolom (desktop)
- Badge "Utama" pada gambar pertama
- Sidebar info & tips

### Form Edit
- Existing images grid
- Card per gambar dengan actions
- Primary badge visual
- Upload new images section
- Metadata info panel

### Animations
- Image preview fade in
- Delete animation fade out
- Loading states pada buttons
- SweetAlert transitions

## 🔒 Security

### Authorization
```python
if 'user_id' not in session or session.get('role') != 'admin':
    flash('Anda harus login sebagai admin', 'danger')
    return redirect(url_for('auth.login'))
```

### File Upload Security
1. **Extension Whitelist**: Hanya allow image extensions
2. **Secure Filename**: `secure_filename()` dari werkzeug
3. **UUID Generation**: Prevent filename conflicts
4. **Directory Creation**: Safe path handling dengan `os.makedirs(exist_ok=True)`

### Validation
**Client-side (JavaScript)**:
- Required fields
- Number validation (harga, stok >= 0)
- File type checking

**Server-side (Python)**:
- Empty field check
- File extension validation
- Database constraint checking
- Try-catch error handling

## 🎭 User Experience

### Loading States
```javascript
submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Menyimpan...');
```

### Flash Messages
```python
flash(f'Produk berhasil ditambahkan dengan {uploaded_count} gambar', 'success')
```

### Error Handling
```python
try:
    produk_id = produk_model.create(data)
except Exception as e:
    flash(f'Gagal menambahkan produk: {str(e)}', 'danger')
```

## 📊 Model Methods

### Produk Model
```python
get_all()                    # List produk + kategori + gambar utama
get_by_id(id)               # Detail produk + kategori
get_images(produk_id)       # Semua gambar produk
create(data)                # Insert produk baru
update(id, data)            # Update produk
delete(id)                  # Delete produk (cascade)
add_image(id, file, is_primary)  # Insert gambar
delete_image(image_id)      # Delete gambar
set_primary_image(produk_id, image_id)  # Set primary
get_all_kategoris()         # List kategori untuk dropdown
```

## 🐛 Error Handling

### Upload Errors
```python
if file and allowed_file(file.filename):
    filename = save_upload_file(file)
    if filename:
        produk_model.add_image(produk_id, filename, is_primary)
```

### Delete Errors
```python
try:
    success = produk_model.delete(id)
    if success:
        # Delete files
        for img in images:
            filepath = os.path.join(UPLOAD_FOLDER, img['gambar_url'])
            if os.path.exists(filepath):
                os.remove(filepath)
except Exception as e:
    return jsonify({'success': False, 'message': str(e)}), 500
```

## 📱 Responsive Design

### Breakpoints
- **Desktop**: Grid 4 kolom gambar
- **Tablet**: Grid 3 kolom gambar
- **Mobile**: Grid 2 kolom gambar

### Table Responsive
```html
<div class="table-responsive">
    <table class="table table-bordered">
```

## 🚀 Performance

### Image Optimization Tips
1. Compress images sebelum upload
2. Gunakan format WEBP untuk size lebih kecil
3. Resize ke max width/height yang reasonable
4. Lazy loading untuk thumbnail list

### Database Query
- JOIN dengan kategori di 1 query
- Subquery untuk gambar utama
- Index pada foreign keys

## 🔄 Workflow

### Add Product Flow
```
User → Form Tambah → Fill Data → Select Images → Preview → Submit
  ↓
Controller → Validate → Save Product → Upload Images → Set Primary
  ↓
Database → Insert barangs → Insert gambar_barangs (multiple)
  ↓
Storage → Save files → Generate UUID filename
  ↓
Response → Flash Success → Redirect to List
```

### Edit Product Flow
```
User → List → Click Edit → Load Form + Existing Images
  ↓
Update Data → Delete Images (optional) → Upload New (optional) → Set Primary
  ↓
Controller → Update barangs → Delete old images → Insert new images
  ↓
Storage → Remove files → Save new files
  ↓
Response → Flash Success → Redirect to List
```

## 📚 Dependencies

```
Flask >= 2.3.0
MySQLdb / PyMySQL
Werkzeug (secure_filename)
UUID (Python built-in)
jQuery 3.x
DataTables 1.10+
Bootstrap 4.x
Font Awesome 5.x
SweetAlert2 11.x
```

## 🧪 Testing Checklist

- [x] List produk tampil dengan data dari DB
- [x] Thumbnail gambar tampil correct
- [x] Tambah produk tanpa gambar
- [x] Tambah produk dengan 1 gambar
- [x] Tambah produk dengan multiple gambar
- [x] Preview gambar sebelum upload
- [x] Gambar pertama jadi primary
- [x] Edit produk data only
- [x] Delete individual image
- [x] Set gambar jadi primary
- [x] Upload gambar baru di edit
- [x] Delete produk cascade
- [x] File storage validation
- [x] Authorization admin only
- [x] DataTables search & sort
- [x] Responsive layout

## 💡 Tips & Best Practices

### Upload Best Practices
1. Validasi file size (max 5MB recommended)
2. Compress images sebelum save
3. Generate thumbnail untuk list
4. Backup folder gambar_produk

### Database Best Practices
1. CASCADE delete untuk orphan cleanup
2. Index pada foreign keys
3. Transaction untuk multiple operations
4. Backup database regular

### Code Best Practices
1. Separate concerns (Model-Controller-View)
2. Error handling comprehensive
3. Validation di client & server
4. Secure file handling
5. SQL injection prevention (parameterized queries)

## 🔮 Future Enhancements

1. **Image Optimization**: Auto-resize & compress
2. **Bulk Operations**: Delete/update multiple produk
3. **Image Zoom**: Lightbox preview gambar
4. **Drag & Drop Upload**: Better UX
5. **Crop & Edit**: Image editor inline
6. **Export Data**: CSV, Excel, PDF
7. **Import Data**: Bulk import dari Excel
8. **API REST**: JSON API untuk mobile app
9. **Search Filters**: Advanced filtering
10. **Barcode/QR**: Generate & scan

---

**Created**: December 17, 2025  
**Author**: Erik  
**Version**: 1.0  
**Status**: Production Ready ✅
