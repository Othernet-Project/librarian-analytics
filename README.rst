===================
librarian-analytics
===================

An endpoint for collecting usage information and periodically sending the
accumulated data to the analytics server.

Installation
------------

The component has the following dependencies:

- librarian-core_
- librarian-filemanager_

To enable this component, add it to the list of components in librarian_'s
`config.ini` file, e.g.::

    [app]
    +components =
        librarian_analytics
