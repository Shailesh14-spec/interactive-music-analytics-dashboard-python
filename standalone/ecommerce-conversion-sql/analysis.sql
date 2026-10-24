-- visitor_type
SELECT VisitorType AS segment,COUNT(*) AS sessions,SUM(Revenue) AS conversions,AVG(Revenue) AS conversion_rate FROM sessions GROUP BY VisitorType ORDER BY sessions DESC;

-- month
SELECT Month AS segment,COUNT(*) AS sessions,SUM(Revenue) AS conversions,AVG(Revenue) AS conversion_rate FROM sessions GROUP BY Month ORDER BY sessions DESC;

-- traffic
SELECT TrafficType AS segment,COUNT(*) AS sessions,SUM(Revenue) AS conversions,AVG(Revenue) AS conversion_rate FROM sessions GROUP BY TrafficType ORDER BY sessions DESC;

-- weekend
SELECT Weekend AS segment,COUNT(*) AS sessions,SUM(Revenue) AS conversions,AVG(Revenue) AS conversion_rate FROM sessions GROUP BY Weekend ORDER BY sessions DESC;
