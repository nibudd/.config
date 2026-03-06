-- fuzzy finder
return {
  'nvim-telescope/telescope.nvim',
  version = "*",
  -- or                              , branch = '0.1.x',
  dependencies = { 'nvim-lua/plenary.nvim' },
  config = function()
    local builtin = require('telescope.builtin')

    vim.keymap.set('n', '<leader>ff', builtin.find_files, { desc = "find files, respecting .gitignore" })

    -- list buffers in order of last used
    vim.keymap.set('n', '<leader>ls', function()
        builtin.buffers({ sort_mru = true })
      end,
      { desc = "list active buffers ordered by most recently used" }
    )

    -- live grep
    vim.keymap.set('n', '<leader>lg', builtin.live_grep, { desc = "live grep, respecting .gitignore" })
    vim.keymap.set('n', '<leader>lf', function()
      builtin.live_grep({ additional_args = { "--no-ignore" }, prompt_title = "Live Grep (no ignore)"})
    end,
      { desc = "live grep, ignoring .gitignore" }
    )

    -- word (under cursor) grep
    vim.keymap.set("n", "<leader>wg", function()
        builtin.live_grep({ default_text = vim.fn.expand("<cword>") })
      end,
      { desc = "open live grep with the word under the cursor" }
    )

    require('telescope').load_extension('fzf')

    -- more options @ https://github.com/nvim-telescope/telescope.nvim?tab=readme-ov-file#default-mappings
  end
}
