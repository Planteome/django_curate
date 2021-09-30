# Global set of choices to use in models

# approval actions
APPROVE = 1
REJECT = 2
MORE_INFO = 3
INITIAL = 4

APPROVAL_ACTION_CHOICES = (
    (APPROVE, "Approve"),
    (REJECT, "Reject"),
    (MORE_INFO, "More info requested"),
    (INITIAL, "Initial request, awaiting moderator")
)

# approval states
PENDING = 1
APPROVED = 2
REJECTED = 3

APPROVED_STATE_CHOICES = (
    (PENDING, "Pending"),
    (APPROVED, "Approved"),
    (REJECTED, "Rejected"),
)
