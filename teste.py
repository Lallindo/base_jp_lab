from base_jp_lab.Objects import Access, decrypt_msg

a = Access('root', '', 'localhost', '3306', 'jp_bd')
r = a.custom_select_query('SELECT * FROM apis WHERE id_api = 5')[0]
print(decrypt_msg(r[8], 'amazon'))