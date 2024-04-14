return {
    'nvim-telescope/telescope.nvim',
    tag = '0.1.6',
    -- or                              , branch = '0.1.x',
    dependencies = { 'nvim-lua/plenary.nvim' },
    config = function()
        local builtin = require('telescope.builtin')

        vim.keymap.set('n', '<leader>ff', builtin.find_files, {})
        vim.keymap.set('n', '<leader>gf', builtin.git_files, {})

        -- list buffers
        vim.keymap.set('n', '<leader>ls', builtin.buffers, {})

        -- live grep 
        vim.keymap.set('n', '<leader>lg', builtin.live_grep, {})

        -- word (under cursor) grep
        vim.keymap.set("n", "<leader>wg", function()
            builtin.live_grep({ default_text = vim.fn.expand("<cword>") })
        end)

        -- more options @ https://github.com/nvim-telescope/telescope.nvim?tab=readme-ov-file#default-mappings
    end
}
