-- super-powerful tool for adding/changing/deleting surrounding pairs
return {
    "kylechui/nvim-surround",
    version = "*", -- Use for stability; omit to use `main` branch for the latest features
    event = "VeryLazy",
    config = function()
        require("nvim-surround").setup({
            -- custom function for indentation of multiline surrounds
            indent_lines = function(start, stop)
                local base = (start > 1) and vim.fn.indent(start - 1) or 0
                local sw = vim.fn.shiftwidth()
                for i = start, stop do
                    local trimmed = vim.fn.getline(i):gsub("^%s*", "")
                    local is_closing = trimmed:match("^[%)%]%}]")
                    local target = is_closing and base or (base + sw)
                    vim.fn.setline(i, string.rep(" ", target) .. trimmed)
                end
            end,
        })
    end
}
