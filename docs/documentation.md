Alur aplikasi purchase app

1.	User membuat purchase event
2.	User membeli barang dari petani lalu user membuat purchase order
3.	User memasukkan barang. Apa saja yang dibeli di purchasemorder line
4.	User memberikan barcode di setiap barang yang dibeli
5.	User mencetak nota dari po untuk diberikan ke petani
6.	Petani membawa nota ke cashier untuk menerima pembayaran
7.	Cashier menscan nota untuk mengarahkan ke po dan menset po menjadi paid
8.	User membuat delivery order untuk mengirimkan barang

Purchase App Rules
1. User hanya boleh membeli barang dari petani yang barangnya ada di commodityitem dan purchase order line odoo
2. Funds di payment hasil compute dari debit dan credit payments, debit digunakan apabila menambahka uang ke dalam pe, credit digunakan apabila mengeluarkan uang atau membayar ke petani
3. Satu purchase order odoo bisa terdiri dari banyak pe (purchase event), satu pe hanya boleh untuk satu PO odoo
4. satu purchase order (purchase app) satu petani
5. Tabel logging digunakan untuk mengecek apakah user terhubung ke server (user menginputkan sesuatu ke tabel logging)

Standard Controller tridir dari list view, create, edit, form view, Delete
Gambar di download, Tambahkan scanner, print ke printer nota via bluetotttyh, konsep crud sama dengan websol


