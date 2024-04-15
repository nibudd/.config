-- super-powerful tool for adding/changing/deleting surrounding pairs
return {
    "kylechui/nvim-surround",
    version = "*", -- Use for stability; omit to use `main` branch for the latest features
    event = "VeryLazy",
    config = function()
        require("nvim-surround").setup({
            -- Configuration here, or leave empty to use defaults
            -- recommended to install `nvim-treesitter/nvim-treesitter-textobjects`
            -- to make configuration easier
        })
    end
}
