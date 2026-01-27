-- git branch and commit graph viewer
return {
    "rbong/vim-flog",
    dependencies = {
        "tpope/vim-fugitive",
    },
    config = function ()
        vim.keymap.set("n", "<leader>gl", "<cmd>Flog<CR>")
    end
}
