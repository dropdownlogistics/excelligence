content = open('src/app/page.jsx', encoding='utf-8').read()
old = '          .af-hero-grid { flex-direction: column !important; }'
new = '          .af-hero-grid { flex-direction: column-reverse !important; }'
fixed = content.replace(old, new)
print('patched:', old in content)
open('src/app/page.jsx', 'w', encoding='utf-8').write(fixed)
print('done')
