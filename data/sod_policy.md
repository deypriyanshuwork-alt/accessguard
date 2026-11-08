# Segregation of Duties Policy (synthetic company policy)

## Purpose and Scope
This policy governs the purchase-to-pay process. Every purchase order (PO) passes through five steps: creation, approval, goods receipt, invoice posting and payment posting. The aim is that no single person controls enough of this chain to commit and hide an error or fraud. Each step should be handled by an appropriate person.

## Roles and Permissions
PO_CREATOR may create purchase orders. PO_APPROVER may approve purchase orders. WAREHOUSE posts goods receipts. AP_CLERK posts supplier invoices. PAYMENT_PROCESSOR posts payments. VENDOR_ADMIN creates and maintains vendor master records.

## Access Risk Versus Violation
A user who holds two conflicting roles, for example PO_CREATOR together with PAYMENT_PROCESSOR, represents an access risk that should be reported for role clean-up. Holding conflicting roles is NOT a violation of a purchase order by itself. A violation exists only when the conflicting access was actually used on the same PO or the same vendor. When reviewing a PO, compare the user ids in each step. Do not flag a PO merely because one of the users holds conflicting roles.

## Rule R1 SOD_CREATE_PAY: Creator Must Not Pay
The user who created a purchase order must not post the payment for that same purchase order. If the user id on the Created step is identical to the user id on the Payment posted step, the PO violates rule R1 and the violation type is SOD_CREATE_PAY. If the two user ids are different, rule R1 is satisfied.

## Rule R2 SELF_APPROVAL: Creator Must Not Approve
The user who created a purchase order must not approve it. If the user id on the Created step is identical to the user id on the Approved step, the PO violates rule R2 and the violation type is SELF_APPROVAL. If the two user ids are different, rule R2 is satisfied.

## Rule R3 VENDOR_CREATE_PAY: Vendor Creator Must Not Pay That Vendor
The user who created a vendor record must not post payments to that vendor. If the user who created the vendor, shown in the context line, is the same user who posted the payment, the PO violates rule R3 and the violation type is VENDOR_CREATE_PAY.

## Rule R4 MISSING_APPROVAL: Approval Is Mandatory
Every purchase order must have an Approved step before payment is posted. If the list of steps contains no Approved step, the PO violates rule R4 and the violation type is MISSING_APPROVAL, even when every other step looks normal. Count the steps carefully: a normal PO has five steps, and a PO with only four steps and no approval is a violation.

## Rule R5 SPLIT_BELOW_THRESHOLD: Splitting Payments
The approval limit is INR 50,000. Splitting one purchase into several smaller ones to stay under the limit is prohibited. Flag a PO as SPLIT_BELOW_THRESHOLD only when the context line shows three or more other POs by the same creator to the same vendor within 7 days AND the amount is within 10 percent below the limit, that is between INR 45,000 and INR 49,999. A single PO near the limit, or only one or two other POs, is not enough to flag.

## Review Procedure
Step 1: list the user at each step. Step 2: check rules R1, R2 and R3 by comparing user ids; identical ids mean a violation. Step 3: check rule R4 by confirming an Approved step exists. Step 4: check rule R5 using the context line. Step 5: if no rule is broken, the violation type is NONE.

## Reporting
State the answer as JSON with a short reason that names the rule and the users involved, a violation flag, and the violation type code. Use NONE when the PO complies with the policy.
