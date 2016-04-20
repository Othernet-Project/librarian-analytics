Librarian analytics overview
============================

Librarian provides some basic analytics capability via the `librarian-analytics
<https://github.com/Outernet-Project/librarian-analytics>`_ component.

The analytics component is open-source and can be inspected for potential
privacy and security issues.

.. contents::

User controls
-------------

Transmission of analytics data can be disabled in the settings panel and the
software stop collecting and transmitting the data.

Performing a factory reset via shell access will change the device ID.

How the information is relayed to the server
--------------------------------------------

The information is relayed in one of two ways:

- over the Internet (if receiver has Internet access)
- manually by retrieving the data from the settings interface and sending it to
  Outernet

After a successful transmission of the analytics data over the Internet, the
local analytics data is permanently destroyed to free storage space. When data
is downloaded, the locally stored data is *not* removed.

Note that if the server receives the transmitted data, but the same data had
previously also been downloaded and manually fed into the server, the server
will prevent duplication of the data, so feeding the server with manually
downloaded data is a safe operation.

What information is collected
-----------------------------

The analytics information is limited strictly to content consumption and it
does not measure anything other than simple access count (it's basically a
click-counter).

The clicks are associated with browser data such as the agent type (mobile,
tablet, desktop, other) and OS type (Windows, Linux, Mac, etc), as well as the
timing information and user's timezone as derived from the browser information.

The clicks are classified based on the trigger and can be one of the following:

- click on a file in the file list
- click on a folder in the file list
- click on a gallery thumbnail
- click on an audio playlist item
- click on a video playlist item
- click on the download link (both in file list and in details panel)

Each click will also be associated with a file or folder path that is hashed
using MD5 has algorithm. The hashes will be correlated to actual paths in the
analytics database on the server. This means that paths that are not in the
analytics database (e.g., user-added files, bundled content that has never been
broadcast, and similar) **cannot be tracked**.

Each browser is given a unique ID which is valid until the browser's cookies
are removed. This means that individual browsers can be tracked, although it is
not possible to track actual users behind the browser.

When the data is transmitted, the receiver ID is also sent along with the data,
and therefore, all analytics events from a single receiver can be analyzed in
isolation.

How the information is collected
--------------------------------

The information is collected by submitting the analytics data from the browser
to the receiver using JavaScipt (AJAX). The information is *not* submitted when
JavaScript is not available on the browser.

Storage and bandwidth characteristics
-------------------------------------

A receiver will attempt to transmit the data every 30 minutes and a maximum of
500 data points will be transferred on each attempt. The following table gives
an overview of the number of transmissions and transmitted data points over the
course of different periods of time.

==========================================  ===================================
Data points per transmission (max)          500
------------------------------------------  -----------------------------------
Transmissions / hour                        2
------------------------------------------  -----------------------------------
Transmissions / day                         48
------------------------------------------  -----------------------------------
Transmissions / month                       1,440
------------------------------------------  -----------------------------------
Data points / hour (max)                    1,000
------------------------------------------  -----------------------------------
Data points / day (max)                     24,000
------------------------------------------  -----------------------------------
Data points / month (max)                   720,000
==========================================  ===================================

The 720,000 data points is the absolute maximum that can be transmitted over 30
days. A receiver whose users generate over 720,000 data points will not be able
to keep up and an irrecoverable lag will be created between creation of new
data points and their transmission to the analytics server. In such cases,
manually downloading the analytics data and feeding it into the server is the
only solution.

The following table gives an overview of bandwidth consumption for each
transmission. The totals over a period of a month are given for the ideal
conditions in which all transmissions would succeed.

==========================================  ===================================
Data points                                 33 bytes / data point
------------------------------------------  -----------------------------------
Device ID                                   16 bytes
------------------------------------------  -----------------------------------
Networking overhead (est)                   20%
------------------------------------------  -----------------------------------
Total for 50 data points (est)              2KB
------------------------------------------  -----------------------------------
Total for 100 data points (est)             3.9KB
------------------------------------------  -----------------------------------
Total for 200 data points (est)             7.8KB
------------------------------------------  -----------------------------------
Total for 500 data points (est)             19.4KB 
------------------------------------------  -----------------------------------
One month @ 50 data points / tsm (est)      2.8MB
------------------------------------------  -----------------------------------
One month @ 100 data points / tsm (est)     5.5MB
------------------------------------------  -----------------------------------
One month @ 200 data points / tsm (est)     11MB
------------------------------------------  -----------------------------------
One month @ 500 data points / tsm (est)     27.3MB
==========================================  ===================================

Analytics data is stored as binary data. Rough estimate is that around 60 bytes
of data is consumed per data point. The maximum practical number of data points
of 720,000 data points would around 42MB of disk space would be used. The
software is configured to perform automatic removal of old data points once the
database has more than 3.7M data points, so an estimated maximum of 220MB of
disk space would be consumed by analytics data.

Downloading the data does not affect disk space consumption and there is no
manual clean-up option.

Data usage examples
^^^^^^^^^^^^^^^^^^^

On a receiver used by 20 users, that has Internet 20% of the time, with 20%
failure rate on transmissions:

==========================================  ===================================
Maximum possible transmissions per month    230
------------------------------------------  -----------------------------------
Maximum possible data points transferred    115,000
------------------------------------------  -----------------------------------
Maximum avg data points per user per month  5750
------------------------------------------  -----------------------------------
Maximum avg data points per user per day    191.6
==========================================  ===================================

Remember that each data point represents a single user action in the Librarian
interface.

Analysis of analytics data
--------------------------

There is currently no dashboard interface for the analytics data. The database
can be dumped in SQL format and analyzed off-site, or the Outernet staff may
analyze the data by accessing the database.
