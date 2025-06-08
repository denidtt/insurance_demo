-- Assumption and Considerations in the query

-- this query is calcluated assuming the comparison is asked for 
-- the total premium received for the most recent policy   -vs-  the average of premium received for all other policies grouped togther.
-- grouping is done per user ,based on the user_id
-- the returning polcies logic is first policy vs all other policies , 
-- In case that assumption is in-correct just changing the rank condition will render the correct answer 
-- filtered for only paid premiums 


WITH sum_per_policy AS (
    SELECT policy_number, SUM(total_amount) AS total_amount
    FROM invoice
    WHERE status = 'paid'
    GROUP BY policy_number
),
ranked_policies AS (
    SELECT 
        sp.policy_number,
        sp.total_amount,
        p.user_id,
        p.product,
        p.effective_date,
        ROW_NUMBER() OVER (PARTITION BY p.user_id ORDER BY p.effective_date DESC) AS RN
    FROM policy p
    JOIN sum_per_policy sp ON p.policy_number = sp.policy_number
),
returning_policies AS (
    SELECT 
        user_id,
        ROUND(SUM(total_amount) / COUNT(policy_number), 2) AS returningpolicies
    FROM ranked_policies
    WHERE RN > 1
    GROUP BY user_id
)
SELECT 
    A.user_id,
    A.total_amount AS first_policy,
    B.returningpolicies
FROM ranked_policies A
LEFT JOIN returning_policies B ON A.user_id = B.user_id
WHERE A.RN = 1 and   A.user_id='28b52674-9558-4938-bdf1-5927e41e3760';