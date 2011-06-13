source /etc/vim/vimrc
source ~/.vimrc
let g:session_autosave = 'no'
let g:session_directory = '.ide_data//'
map <F8> <Esc>:SaveSession editor
map <F5> <Esc>:OpenSession editor