local M = {}

local function window_option(name)
	local result = vim.system({ "tmux", "show-options", "-wv", "-t", vim.env.TMUX_PANE, name }, { text = true }):wait()
	if result.code ~= 0 then
		error("TODO: Update Prose nibflow: cannot read " .. name .. ": " .. vim.trim(result.stderr))
	end
	return vim.trim(result.stdout)
end

local function read_layout(name)
	local path = vim.api.nvim_get_runtime_file("layouts/" .. name .. ".json", false)[1]
	if path == nil then
		error("TODO: Update Prose nibflow: no layout file for " .. name)
	end
	return vim.json.decode(table.concat(vim.fn.readfile(path), "\n"))
end

function M.start()
	local task_key = window_option("@nibflow_task")
	local layout = read_layout(window_option("@nibflow_layout"))
	require("nibflow.layout").build(layout, task_key)
end

return M
