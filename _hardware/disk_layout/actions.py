from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self, serviceObj):

        def formatHRD():
            """
            give the right format to hrd
            """
            res = serviceObj.hrd.get('disk.available')
            if isinstance(res,basestring):
                disks = res.split('\n')
                serviceObj.hrd.set('disk.available', disks)

        j.actions.start(name="formatHRD",description='formatHRD', action=formatHRD, stdOutput=False, serviceObj=serviceObj)

    def configure(self, serviceObj):
        disks = serviceObj.hrd.getList('disk.available')

        partitions = []
        for disk in disks:
            if self._hasFreeSpace(disk):
                self._createPatition(disk, 'primary')
                partitions.append(partitionName)
        for i in xrange(0,len(partitions)-1,2):
            targets = [partitions[i], partitions[i+1]]
            self._createFileSystem(targets)

    def removedata(self, serviceObj):
        pass

    def _getFreeSpace(self, disk):
        """
        find fee space on a disk
        returns : tuple (start,end,size) of the free space of the disk
        """
        if not isinstance(disk, basestring):
            j.events.inputerror_critical("disk should be a string of the form /dev/sdx")

        """
        the command return something like
        1:17.4kB:16.0GB:16.0GB:free;
        1:17.4kB:16.0GB:16.0GB:free;
        """
        cmd = "parted -m %s print free | tail -n -1" % disk
        retcode,out = j.do.execute(cmd)

        if out == '':
            return []

        result = []
        lines = out.split('\n')
        for line in lines:
            _, start, end, size, _ = tuple(line.split(":"))
            result.append((start,end,size))

        return result

    def _hasFreeSpace(self, disk):
        cmd = "parted -m %s print free | tail -n -1" % disk
        retcode,out = j.do.execute(cmd)
        return (out != '')

    def _getLastPartition(self, disk):
        """
        return the name of the last partition of a disk
        """
        cmd = "parted -m %s print | tail -n 1" % disk
        _, out, err = j.do.execute(cmd)
        return "$s%s" % (disk, out.split(':')[0])

    def _createPatition(self, disk, type):
        """
        create a partition on disk and use all free space
        type can be primary or logical
        returns : name of the created partition
        """

        if type not in ['primary', 'logical']:
            j.events.inputerror_critical('type can only be primary or logical, it\'s %s' % type)

        cmd = "parted -s -a optimal %s mkpart %s 2 100%" % (disk, type)
        j.do.execute(cmd)
        return  self._getLastPartition(disk)


    def _createFileSystem(self, partitions):
        """
        create RAID1 btrfs file system on partitions.
        args : partitions is a list of two partitions
        """
        if len(partitions) != 2:
            j.events.inputerror_critical("partitions should have a lenght of 2.")
        cmd = "mkfs.btrfs -draid1 -mraid1 %s" % " ".join(partitions)
        j.do.execute(cmd)

    def _extractDisk(partition):
        """
        extract the disk name from a partition name
        from /dev/sda1 return /dev/sda
        """
        return partition[:8]