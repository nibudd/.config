local M = {}

function M.open(win, task_key)
	local buf = vim.api.nvim_create_buf(false, true)
	vim.api.nvim_buf_set_lines(buf, 0, -1, false, { "overview", task_key })
	vim.api.nvim_win_set_buf(win, buf)
end

return M
