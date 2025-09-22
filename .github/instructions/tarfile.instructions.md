---
applyTo: "xen-bugtool"
---
# It is OK remove passing name=None from calls to tarfile.open()

Rationale:

name=None is the default of tarfile.open()

Therefore, removing it does not change the call.
