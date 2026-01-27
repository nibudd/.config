-- test runner framework with pytest support
return {
  {
    "nvim-neotest/neotest",
    dependencies = {
        "nvim-neotest/nvim-nio",
        "nvim-lua/plenary.nvim",
        "antoinemadec/FixCursorHold.nvim",
        "nvim-treesitter/nvim-treesitter",
        "nvim-neotest/neotest-python",
    },
    config = function()
      require("neotest").setup({
        adapters = {
          require("neotest-python")({
            dap = {
              justMyCode = false,
            },
            args = { "--log-level", "DEBUG", "--quiet" },
            runner = "pytest",
          })
        }
      })
      local neotest = require("neotest")

      vim.keymap.set("n", "<Leader>tm", neotest.run.run) -- run nearest test
      vim.keymap.set("n", "<Leader>tf", function () neotest.run.run(vim.fn.expand('%')) end) -- run the current file
      vim.keymap.set("n", "<Leader>td", function () neotest.run.run({strategy = "dap"}) end) -- debug nearest test
      vim.keymap.set("n", "<Leader>ts", function () neotest.summary.toggle() end)
    end
  },
}
