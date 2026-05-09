locals {
  ai_foundry_name   = coalesce(var.ai_foundry.name, "aif-${var.base_name}-${local.resource_token}")
  base_name_storage = substr(replace(var.base_name, "-", ""), 0, 18)
  location          = var.location
  resource_names = {
    ai_agent_host = coalesce(var.resource_names.ai_agent_host, "ah${var.base_name}agent${local.resource_token}")
  }
  resource_token = random_string.resource_token.result
}
