# template: autosnapshotting

## Description:
This actor template is responsible to create a periodic snapshots on all machines inside the specified VDC.
make sure that ays deamon is started `ays start`

## Schema:

- vdc: vdc that the service will work in.
- startDate: Start date at which the autosnapshotting will start.
- endDate: End date at which the autosnapshotting will end taking those periodic snapshots.
- snapshotInterval: The duration interval at which the service will take snapshots.
- retention: The maximum duration that snapshots are allowed to live before being deleted.
- cleanupInterval: The duration interval at which the service periodically scan and remove any snapshots that're expired.
