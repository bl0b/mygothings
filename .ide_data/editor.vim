" ~/bl0b_dev/mygothings/.ide_data/editor.vim: Vim session script.
" Created by ~/.vim/autoload/xolox/session.vim on 02 juillet 2011 at 23:16:06.
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
badd +1 py/explorer.py
silent! argdel *
set lines=70 columns=156
edit py/explorer.py
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
wincmd _ | wincmd |
split
1wincmd k
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
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
exe 'vert 1resize ' . ((&columns * 1 + 78) / 156)
exe '2resize ' . ((&lines * 22 + 35) / 70)
exe 'vert 2resize ' . ((&columns * 56 + 78) / 156)
exe '3resize ' . ((&lines * 22 + 35) / 70)
exe 'vert 3resize ' . ((&columns * 97 + 78) / 156)
exe '4resize ' . ((&lines * 1 + 35) / 70)
exe 'vert 4resize ' . ((&columns * 90 + 78) / 156)
exe '5resize ' . ((&lines * 43 + 35) / 70)
exe 'vert 5resize ' . ((&columns * 90 + 78) / 156)
exe '6resize ' . ((&lines * 45 + 35) / 70)
exe 'vert 6resize ' . ((&columns * 63 + 78) / 156)
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
let s:l = 35 - ((15 * winheight(0) + 11) / 22)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
35
normal! 03l
wincmd w
argglobal
edit py/shape.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 257 - ((0 * winheight(0) + 11) / 22)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
257
normal! 016l
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
let s:l = 217 - ((0 * winheight(0) + 0) / 1)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
217
normal! 036l
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
let s:l = 420 - ((29 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
420
normal! 049l
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
let s:l = 236 - ((24 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
236
normal! 030l
wincmd w
6wincmd w
exe 'vert 1resize ' . ((&columns * 1 + 78) / 156)
exe '2resize ' . ((&lines * 22 + 35) / 70)
exe 'vert 2resize ' . ((&columns * 56 + 78) / 156)
exe '3resize ' . ((&lines * 22 + 35) / 70)
exe 'vert 3resize ' . ((&columns * 97 + 78) / 156)
exe '4resize ' . ((&lines * 1 + 35) / 70)
exe 'vert 4resize ' . ((&columns * 90 + 78) / 156)
exe '5resize ' . ((&lines * 43 + 35) / 70)
exe 'vert 5resize ' . ((&columns * 90 + 78) / 156)
exe '6resize ' . ((&lines * 45 + 35) / 70)
exe 'vert 6resize ' . ((&columns * 63 + 78) / 156)
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
1resize 68|vert 1resize 1|2resize 22|vert 2resize 56|3resize 22|vert 3resize 97|4resize 1|vert 4resize 90|5resize 43|vert 5resize 90|6resize 45|vert 6resize 63|
tabnext 1
6wincmd w

" vim: ft=vim ro nowrap smc=128
