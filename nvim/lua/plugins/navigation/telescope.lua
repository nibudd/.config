-- fuzzy finder
return {
  'nvim-telescope/telescope.nvim',
  version = "*",
  dependencies = { 'nvim-lua/plenary.nvim' },
  keys = {
    {
      '<leader>ff',
      function() require('telescope.builtin').find_files() end,
      desc = "find files, respecting .gitignore",
    },
    {
      '<leader>ls',
      function() require('telescope.builtin').buffers({ sort_mru = true }) end,
      desc = "list active buffers ordered by most recently used",
    },
    {
      '<leader>lg',
      function() require('telescope.builtin').live_grep() end,
      desc = "live grep, respecting .gitignore",
    },
    {
      '<leader>lf',
      function()
        require('telescope.builtin').live_grep({
          additional_args = { "--no-ignore" },
          prompt_title = "Live Grep (no ignore)",
        })
      end,
      desc = "live grep, ignoring .gitignore",
    },
    {
      '<leader>wg',
      function()
        require('telescope.builtin').live_grep({ default_text = vim.fn.expand("<cword>") })
      end,
      desc = "open live grep with the word under the cursor",
    },
  },
  config = function()
    require('telescope').load_extension('fzf')
  end,
}
