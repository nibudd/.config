-- language-based highlighting
return {
    {
        "nvim-treesitter/nvim-treesitter",
        build = ":TSUpdate",
        config = function()
            require("nvim-treesitter.configs").setup({
                ensure_installed = {
                    "bash",
                    "javascript",
                    "lua",
                    "python",
                    "sql",
                    "typescript",
                    "vim",
                    "vimdoc",
                },
                sync_install = true,

                additional_vim_regex_highlighting = false,
                auto_install = true,
                highlight = { enable = true },
                indent = { enable = true },
            })
        end
    },
}
