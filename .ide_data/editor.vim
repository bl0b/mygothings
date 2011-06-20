" ~/bl0b_dev/mygothings/.ide_data/editor.vim: Vim session script.
" Created by ~/.vim/autoload/xolox/session.vim on 19 juin 2011 at 20:09:28.
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
badd +1 py/shape.py
badd +243 py/goban.py
silent! argdel *
set lines=70 columns=140
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
exe 'vert 1resize ' . ((&columns * 13 + 70) / 140)
exe '2resize ' . ((&lines * 7 + 35) / 70)
exe 'vert 2resize ' . ((&columns * 126 + 70) / 140)
exe '3resize ' . ((&lines * 1 + 35) / 70)
exe 'vert 3resize ' . ((&columns * 79 + 70) / 140)
exe '4resize ' . ((&lines * 58 + 35) / 70)
exe 'vert 4resize ' . ((&columns * 79 + 70) / 140)
exe '5resize ' . ((&lines * 60 + 35) / 70)
exe 'vert 5resize ' . ((&columns * 46 + 70) / 140)
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
let s:l = 222 - ((5 * winheight(0) + 3) / 7)
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
normal! 034l
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
let s:l = 284 - ((29 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
284
normal! 013l
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
let s:l = 36 - ((27 * winheight(0) + 30) / 60)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
36
normal! 018l
wincmd w
5wincmd w
exe 'vert 1resize ' . ((&columns * 13 + 70) / 140)
exe '2resize ' . ((&lines * 7 + 35) / 70)
exe 'vert 2resize ' . ((&columns * 126 + 70) / 140)
exe '3resize ' . ((&lines * 1 + 35) / 70)
exe 'vert 3resize ' . ((&columns * 79 + 70) / 140)
exe '4resize ' . ((&lines * 58 + 35) / 70)
exe 'vert 4resize ' . ((&columns * 79 + 70) / 140)
exe '5resize ' . ((&lines * 60 + 35) / 70)
exe 'vert 5resize ' . ((&columns * 46 + 70) / 140)
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
1resize 68|vert 1resize 13|2resize 7|vert 2resize 126|3resize 1|vert 3resize 79|4resize 58|vert 4resize 79|5resize 60|vert 5resize 46|
tabnext 1
5wincmd w

" vim: ft=vim ro nowrap smc=128
