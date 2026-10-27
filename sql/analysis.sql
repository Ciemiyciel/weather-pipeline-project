
-- 1. Średnia temperatura w każdym mieście
SELECT
    city,
    ROUND(AVG(temperature_2m), 2) AS avg_temperature
FROM weather
GROUP BY city
ORDER BY avg_temperature DESC;

-- 2. Łączne opady w badanym okresie
SELECT
    city,
    ROUND(SUM(precipitation), 2) AS total_precipitation
FROM weather
GROUP BY city
ORDER BY total_precipitation DESC;

-- 3. Opady w poszczególnych dniach
SELECT
    city,
    CAST(timestamp AS DATE) AS day,
    ROUND(SUM(precipitation), 2) AS daily_precipitation
FROM weather
GROUP BY city, CAST(timestamp AS DATE)
ORDER BY day, city;

-- 4. Maksymalna prędkość wiatru w każdym mieście
SELECT
    city,
    ROUND(MAX(wind_speed_10m), 2) AS max_wind_speed
FROM weather
GROUP BY city
ORDER BY max_wind_speed DESC;
