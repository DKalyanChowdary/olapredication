--name : only success rides
 SELECT *
FROM ola_rides_july_clean
WHERE Booking_Status = 'Success';

--name :Average distance by vehicle_type
SELECT
    Vehicle_Type,
    AVG(Ride_Distance) AS avg_ride_distance
FROM ola_rides_july_clean
GROUP BY Vehicle_Type; 

--name :Total number of cancelled rides by customers
SELECT
    COUNT(*) AS total_customer_cancellations
FROM ola_rides_july_clean
WHERE Booking_Status = 'Canceled by Customer'; 

--name:Top 5 customers who booked the highest number of rides
SELECT TOP 5
    Customer_ID,
    COUNT(Booking_ID) AS total_rides
FROM ola_rides_july_clean
GROUP BY Customer_ID
ORDER BY total_rides DESC;

--name:The no of rides cancelled by drivers due to personal and car-related issues
SELECT COUNT(*) AS Cancelled_By_Driver_PersonalCar
FROM ola_rides_july_clean
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

--name:maximum and minimum driver ratings for Prime Sedan bookings
SELECT MAX(Driver_Ratings) AS max_driver_rating,MIN(Driver_Ratings) AS min_driver_rating
FROM ola_rides_july_clean
WHERE Vehicle_Type = 'Prime Sedan'; 
--name:rides where payment was made using UPI
SELECT *
FROM ola_rides_july_clean
WHERE Payment_Method = 'UPI';

--name:average customer rating per vehicle type
SELECT
    Vehicle_Type,
    AVG(Customer_Rating) AS avg_customer_rating
FROM ola_rides_july_clean
GROUP BY Vehicle_Type
ORDER BY avg_customer_rating DESC;

--name:Total booking value of rides completed successfully
SELECT
    SUM(Booking_Value) AS total_successful_booking_value
FROM ola_rides_july_clean
WHERE Booking_Status = 'Success';

--name:List all incomplete rides along with the reason
SELECT
    Booking_ID,
    Booking_Status,
    Incomplete_Rides_Reason
FROM ola_rides_july_clean
WHERE Booking_Status <> 'Success';

--name: Revenue by Payment Method
SELECT Payment_Method,
    SUM(Booking_Value) AS total_revenue
FROM ola_rides_july_clean
WHERE Booking_Status = 'Success'
GROUP BY Payment_Method;

--name:list of rides cancelled with reason(notinculde null)
-- Union all three columns into one list
WITH AllReasons AS (
    SELECT Incomplete_Rides_Reason AS Reason
    FROM ola_rides_july_clean
    WHERE Incomplete_Rides_Reason IS NOT NULL
    UNION ALL
    SELECT Canceled_Rides_by_Driver
    FROM ola_rides_july_clean
    WHERE Canceled_Rides_by_Driver IS NOT NULL
    UNION ALL
    SELECT Canceled_Rides_by_Customer
    FROM ola_rides_july_clean
    WHERE Canceled_Rides_by_Customer IS NOT NULL
)
-- Aggregate to get frequency
SELECT Reason, COUNT(*) AS Reason_Count
FROM AllReasons
GROUP BY Reason
ORDER BY Reason_Count DESC;
