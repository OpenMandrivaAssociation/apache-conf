#!/usr/bin/perl
#
## ====================================================================
## The Apache Software License, Version 1.1
##
## Copyright (c) 2000 The Apache Software Foundation.  All rights
## reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##
## 1. Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
##
## 2. Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in
##    the documentation and/or other materials provided with the
##    distribution.
##
## 3. The end-user documentation included with the redistribution,
##    if any, must include the following acknowledgment:
##       "This product includes software developed by the
##        Apache Software Foundation (http://www.apache.org/)."
##    Alternately, this acknowledgment may appear in the software itself,
##    if and wherever such third-party acknowledgments normally appear.
##
## 4. The names "Apache" and "Apache Software Foundation" must
##    not be used to endorse or promote products derived from this
##    software without prior written permission. For written
##    permission, please contact apache@apache.org.
##
## 5. Products derived from this software may not be called "Apache",
##    nor may "Apache" appear in their name, without prior written
##    permission of the Apache Software Foundation.
##
## THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
## WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
## OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
## ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
## USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
## OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
## OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
## SUCH DAMAGE.
## ====================================================================
##
## This software consists of voluntary contributions made by many
## individuals on behalf of the Apache Software Foundation.  For more
## information on the Apache Software Foundation, please see
## <http://www.apache.org/>.
##
## Portions of this software are based upon public domain software
## originally written at the National Center for Supercomputing Applications,
## University of Illinois, Urbana-Champaign.
##
##

## Heavily modified by Jean-Michel Dault <jmdault@mandrakesoft.com>
## for use with in the Avanced Extranet Server.
## This script can now be used with the CustomLogs directive, with a pipe.
## When in combination with SetEnv VLOG <path>, it will write the log file
## in the right place. Also, it splits the log automatically with a year
## and month prefix. Finally, we open and re-close the logfile for every
## log entry. It is slower, but it permits us to check for symlinks, and
## flush the buffers so everything is realtime and we don't lose any entry.

#
# This script will take a combined Web server access
# log file and break its contents into separate files.
# It assumes that the first field of each line is the
# virtual host identity (put there by "%v"), and that
# the logfiles should be named that+".log" in the current
# directory.
#
# The combined log file is read from stdin. Records read
# will be appended to any existing log files.
#

use POSIX qw(:signal_h);

 $sigset = POSIX::SigSet->new(SIGTERM);    # define the signals to block
 $old_sigset = POSIX::SigSet->new;        # where the old sigmask will be kept

 #Block SIGTERM
 unless (defined sigprocmask(SIG_BLOCK, $sigset, $old_sigset)) {
     die "Could not block SIGTERM\n";
 }

 #Unblock
 #unless (defined sigprocmask(SIG_UNBLOCK, $old_sigset)) {
 #    die "Could not unblock SIGTERM\n";
 #}


local $_;
while (<STDIN>) {
    #
    # Get the first token from the log record; it's the
    # identity of the virtual host to which the record
    # applies.
    #
    my ($vhost) = split /\s/;
    #
    # Normalize the virtual host name to all lowercase.
    # If it's blank, the request was handled by the default
    # server, so supply a default name.  This shouldn't
    # happen, but caution rocks.
    #
    $vhost = lc($vhost) or "access";
    #

    s/VLOG=(.*)[\/]*$//;
    my $logs = $1;
    $logs = "/var/log/httpd" if $logs eq "";
    my $date = `date +%Y-%m`;
    chop $date;
    my $filename = "$logs/VLOG-$date-${vhost}.log";
    if (-l $filename) { 
	die "File $filename is a symlink, writing too dangerous, dying!\n";
    }
    local *LOGFILE;
    open LOGFILE, ">>$filename"
            or die("Can't open $logs/$filename");
    #
    # Strip off the first token (which may be null in the
    # case of the default server), and write the edited
    # record to the current log file.
    #
    s/^\S*\s+//;
    print LOGFILE $_;
    close(LOGFILE);
}

exit(0);
