locals {
  ai_search_rbac = { for role in flatten([
    for ak, av in var.ai_search_definition : [
      for rk, rv in av.role_assignments : {
        ai_key          = ak
        rbac_key        = rk
        role_assignment = rv
      }
    ]
  ]) : "${role.ai_key}-${role.rbac_key}" => role }
}
