SELECT
    city,
    CAST(timestamp AS DATE) AS day,
    ROUND(AVG(temperature_2m)::numeric,2) AS avg_temperature,
    ROUND(SUM(precipitation)::numeric,2) AS total_precipitation
FROM weather_observations
GROUP BY city, CAST(timestamp as DATE)
ORDER BY day,city;

SELECT
    city,
    ROUND(AVG(temperature_2m)::numeric, 2) AS avg_temperature,
    RANK() OVER (
        ORDER BY AVG(temperature_2m) DESC
    ) AS temperature_rank
FROM weather_observations
GROUP BY city
ORDER BY temperature_rank;

SELECT
    city,
    timestamp,
    temperature_2m,
    ROUND(
        AVG(temperature_2m) OVER (
            PARTITION BY city
            ORDER BY timestamp
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        )::numeric,
        2
    ) AS moving_avg_24h
FROM weather_observations
ORDER BY city, timestamp;

WITH daily_weather AS (
    SELECT
        city,
        CAST(timestamp AS DATE) AS day,
        AVG(temperature_2m) AS avg_temperature,
        SUM(precipitation) AS total_precipitation
    FROM weather_observations
    GROUP BY city, CAST(timestamp AS DATE)
)
SELECT *
FROM daily_weather
WHERE total_precipitation > 0
ORDER BY total_precipitation DESC;