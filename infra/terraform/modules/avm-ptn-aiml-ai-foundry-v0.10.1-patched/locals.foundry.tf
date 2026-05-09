locals {
  foundry_default_role_assignments = {
    #holding this variable in the event we need to add static defaults in the future.
  }
  foundry_role_assignments = merge(
    local.foundry_default_role_assignments,
    var.ai_foundry.role_assignments
  )
  role_definition_resource_substring = "providers/Microsoft.Authorization/roleDefinitions"
}
