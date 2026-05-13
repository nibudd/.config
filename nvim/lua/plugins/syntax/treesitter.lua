-- language-based highlighting
local languages = {
    "bash",
    "css",
    "html",
    "javascript",
    "lua",
    "python",
    "sql",
    "typescript",
    "vim",
    "vimdoc",
    "vue",
}

return {
    {
        "nvim-treesitter/nvim-treesitter",
        lazy = false,
        build = ":TSUpdate",
        config = function()
            require("nvim-treesitter").install(languages)

            vim.api.nvim_create_autocmd("FileType", {
                pattern = languages,
                callback = function()
                    vim.treesitter.start()
                    vim.bo.indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
                end,
            })
        end
    },
}
