-- ** Aggregate (COUNT, AVG, etc.) + Sliding time window **

-- Performs function on the aggregate rows over a 10 second sliding window for a specified column. 

--          .----------.   .----------.   .----------.              
--          |  SOURCE  |   |  INSERT  |   |  DESTIN. |              
-- Source-->|  STREAM  |-->| & SELECT |-->|  STREAM  |-->Destination
--          |          |   |  (PUMP)  |   |          |              
--          '----------'   '----------'   '----------'               

-- STREAM (in-application): a continuously updated entity that you can SELECT from and INSERT into like a TABLE
-- PUMP: an entity used to continuously 'SELECT ... FROM' a source STREAM, and INSERT SQL results into an output STREAM

create or replace stream "DESTINATION_SQL_STREAM" (
  "neighborhood" varchar(255),
  "average_sentiment" double
)
;

create or replace pump "STREAM_PUMP" as
insert into "DESTINATION_SQL_STREAM"
select stream "neighborhood",
  avg("sentiment") over thirty_minute_sliding_window as "average_sentiment"
from "SOURCE_SQL_STREAM_001"
where "neighborhood" is not null
window thirty_minute_sliding_window as (
  partition by "neighborhood"
  range interval '30' minute preceding
)
;

