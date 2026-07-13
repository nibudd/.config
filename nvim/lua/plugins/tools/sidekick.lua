-- AI assistant integration with tmux support

-- sidekick's context picker (M.ctx) targets the most-recently-focused window
-- via a `sidekick_visit` timestamp rather than the current window. On a fresh
-- multi-window layout (e.g. a vim-obsession session restore) nothing is stamped
-- yet, so the picker falls back to window-creation order and can grab the wrong
-- buffer -- yielding a "@other-file :L0" reference or a raw selection paste.
-- Stamp the current window before sending so our window always wins the sort.
local function from_here(fn)
  return function()
    vim.w[vim.api.nvim_get_current_win()].sidekick_visit = vim.uv.hrtime()
    fn()
  end
end

return {
  "folke/sidekick.nvim",
  opts = {
    -- add any options here
    cli = {
      mux = {
        backend = "tmux",
        enabled = true,
        create = "split",
      },
    },
  },
  keys = {
    {
      "<tab>",
      function()
        -- if there is a next edit, jump to it, otherwise apply it if any
        if not require("sidekick").nes_jump_or_apply() then
          return "<Tab>" -- fallback to normal tab
        end
      end,
      expr = true,
      desc = "Goto/Apply Next Edit Suggestion",
    },
    {
      "<c-.>",
      function() require("sidekick.cli").toggle() end,
      desc = "Sidekick Toggle",
      mode = { "n", "t", "i", "x" },
    },
    {
      "<leader>aa",
      function() require("sidekick.cli").toggle() end,
      desc = "Sidekick Toggle CLI",
    },
    {
      "<leader>as",
      function() require("sidekick.cli").select() end,
      -- Or to select only installed tools:
      -- require("sidekick.cli").select({ filter = { installed = true } })
      desc = "Select CLI",
    },
    {
      "<leader>ad",
      function() require("sidekick.cli").close() end,
      desc = "Detach a CLI Session",
    },
    {
      "<leader>at",
      from_here(function() require("sidekick.cli").send({ msg = "{this}" }) end),
      mode = { "x", "n" },
      desc = "Send This",
    },
    {
      "<leader>af",
      from_here(function() require("sidekick.cli").send({ msg = "{file}" }) end),
      desc = "Send File",
    },
    {
      "<leader>av",
      from_here(function() require("sidekick.cli").send({ msg = "{selection}" }) end),
      mode = { "x" },
      desc = "Send Visual Selection",
    },
    {
      "<leader>ap",
      from_here(function() require("sidekick.cli").prompt() end),
      mode = { "n", "x" },
      desc = "Sidekick Select Prompt",
    },
    -- Example of a keybinding to open Claude directly
    {
      "<leader>ac",
      function() require("sidekick.cli").toggle({ name = "claude", focus = true }) end,
      desc = "Sidekick Toggle Claude",
    },
  },
}
