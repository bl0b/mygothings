" ~/bl0b_dev/mygothings/.ide_data/editor.vim: Vim session script.
" Created by ~/.vim/autoload/xolox/session.vim on 18 juin 2011 at 12:45:39.
" Open this file in Vim and run :source % to restore your session.

set guioptions=batgirl
silent! set guifont=
if exists('g:syntax_on') != 1 | syntax on | endif
if exists('g:did_load_filetypes') != 1 | filetype on | endif
if exists('g:did_load_ftplugin') != 1 | filetype plugin on | endif
if exists('g:did_indent_on') != 1 | filetype indent on | endif
if !exists('g:colors_name') || g:colors_name != 'torte' | colorscheme torte | endif
set background=dark
call setqflist([])
let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/bl0b_dev/mygothings
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +1 py/sandbox.py
badd +182 py/grid.py
badd +0 py/shape.py
badd +243 py/goban.py
silent! argdel *
set lines=59 columns=119
edit py/shape.py
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
wincmd _ | wincmd |
split
1wincmd k
wincmd w
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd _ | wincmd |
split
1wincmd k
wincmd w
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
exe 'vert 1resize ' . ((&columns * 13 + 59) / 119)
exe '2resize ' . ((&lines * 45 + 29) / 59)
exe 'vert 2resize ' . ((&columns * 105 + 59) / 119)
exe '3resize ' . ((&lines * 1 + 29) / 59)
exe 'vert 3resize ' . ((&columns * 91 + 59) / 119)
exe '4resize ' . ((&lines * 9 + 29) / 59)
exe 'vert 4resize ' . ((&columns * 91 + 59) / 119)
exe '5resize ' . ((&lines * 11 + 29) / 59)
exe 'vert 5resize ' . ((&columns * 13 + 59) / 119)
argglobal
enew
file NERD_tree_1
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 222 - ((34 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
222
normal! 017l
wincmd w
argglobal
edit py/goban.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 179 - ((0 * winheight(0) + 0) / 1)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
179
normal! 035l
wincmd w
argglobal
edit py/grid.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 200 - ((5 * winheight(0) + 4) / 9)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
200
normal! 030l
wincmd w
argglobal
edit py/sandbox.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 316 - ((0 * winheight(0) + 5) / 11)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
316
normal! 04l
wincmd w
2wincmd w
exe 'vert 1resize ' . ((&columns * 13 + 59) / 119)
exe '2resize ' . ((&lines * 45 + 29) / 59)
exe 'vert 2resize ' . ((&columns * 105 + 59) / 119)
exe '3resize ' . ((&lines * 1 + 29) / 59)
exe 'vert 3resize ' . ((&columns * 91 + 59) / 119)
exe '4resize ' . ((&lines * 9 + 29) / 59)
exe 'vert 4resize ' . ((&columns * 91 + 59) / 119)
exe '5resize ' . ((&lines * 11 + 29) / 59)
exe 'vert 5resize ' . ((&columns * 13 + 59) / 119)
tabnext 1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
tabnext 1
1wincmd w
bwipeout
NERDTree ~/bl0b_dev/mygothings
1resize 57|vert 1resize 13|2resize 45|vert 2resize 105|3resize 1|vert 3resize 84|4resize 9|vert 4resize 84|5resize 11|vert 5resize 20|
tabnext 1
2wincmd w

" vim: ft=vim ro nowrap smc=128
