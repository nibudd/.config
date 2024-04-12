return {
  {
    "nvim-treesitter/nvim-treesitter",
    opts = {
      ensured_installed = {
        "go",
        "javascript",
        "json",
        "lua",
        "markdown",
        "markdown_inline",
        "md",
        "python",
        "typescript",
        "yaml",
      }
    },
    build = ":TSUpdate",
    config = function()
      local config = require("nvim-treesitter.configs")
      config.setup({
        auto_install = true,
        highlight = { enable = true },
        indent = { enable = true },
      })
    end
  }
}
