-- Menambahkan kolom gambar pada tabel barangs
ALTER TABLE `barangs` ADD COLUMN `gambar` VARCHAR(255) NULL AFTER `stok`;

-- Update beberapa data sample jika diperlukan
-- UPDATE `barangs` SET `gambar` = 'product-1.jpg' WHERE `id` = 1;
