require("config")

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
    vim.fn.system({
        "git",
        "clone",
        "--filter=blob:none",
        "https://github.com/folke/lazy.nvim.git",
        "--branch=stable", -- latest stable release
        lazypath,
    })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup("plugins", {
    checker = {
        enabled = true,
        frequency = 60 * 60 * 24 -- every 24hrs
    }
}
)

vim.api.nvim_create_augroup('TypescriptReactCommentString', { clear = true })
vim.api.nvim_create_autocmd('FileType', {
  group = 'TypescriptReactCommentString',
  pattern = 'typescriptreact',
  command = 'setlocal commentstring=//\\ %s',
})
