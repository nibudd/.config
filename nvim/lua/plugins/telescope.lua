-- fuzzy finder
return {
    'nvim-telescope/telescope.nvim',
    tag = '0.1.6',
    -- or                              , branch = '0.1.x',
    dependencies = { 'nvim-lua/plenary.nvim' },
    config = function()
        local builtin = require('telescope.builtin')

        vim.keymap.set('n', '<leader>ff', builtin.find_files, {})
        vim.keymap.set('n', '<leader>gf', builtin.git_files, {})

        -- list buffers in order of last used
        vim.keymap.set('n', '<leader>ls', function()
            builtin.buffers({ sort_mru = true })
        end, {})

        -- live grep 
        vim.keymap.set('n', '<leader>lg', builtin.live_grep, {})

        -- word (under cursor) grep
        vim.keymap.set("n", "<leader>wg", function()
            builtin.live_grep({ default_text = vim.fn.expand("<cword>") })
        end)

        require('telescope').load_extension('fzf')

        -- more options @ https://github.com/nvim-telescope/telescope.nvim?tab=readme-ov-file#default-mappings
    end
}
