-- lightweight formatter
return {
  'stevearc/conform.nvim',
  opts = {
    formatters_by_ft = {
      lua = { "stylua" },
      -- Conform will run multiple formatters sequentially
      python = { "ruff_fix", "ruff_format", "ruff_organize_imports" },
      -- Conform will run the first available formatter
      javascript = { "eslint_d" },
      typescript = { "eslint_d" },
    },
    format_on_save = {
      timeout_ms = 500,
      lsp_format = "fallback",
    },
  },
}
