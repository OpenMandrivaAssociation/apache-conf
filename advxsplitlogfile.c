/*
From anders@kalibalik.dk Wed May 22 12:31:55 2002
I have converted the advxsplitlogfile script into C, in order to not
have Perl running on my small server, just for that one simple script.
...
Anders Melchiorsen
*/

#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#define SIZE 1024

int i;
char* m;
char* n;

char in[SIZE];
char vhost[SIZE];
char path[SIZE];
char filename[SIZE];

char date[32];
time_t stamp;

void die(const char* reason)
{
	puts(reason);
	exit(EXIT_FAILURE);
}

int main()
{
	while (!feof(stdin)) {

		// Read a line
		if (!fgets(in, sizeof(in)-1, stdin))
			break;

		// Forget newlines and trailing slashes
		i = strlen(in)-1;
		while (i >= 0 && (in[i] == '\n' || in[i] == '/'))
			in[i--] = 0;

		// Get the first token (vhost name) or a default name
		for (i = 0; in[i] && !isspace(in[i]); ++i)
			vhost[i] = tolower(in[i]);
		vhost[i] = 0;

		// Remove token and any following white space
		while (in[i] && isspace(in[i]))
			++i;
		memmove(in, &in[i], sizeof(in)-i);
		
		// Find user supplied path at the end
		m = in;
		while ((n = strstr(m, "VLOG=")))
			m = n+5;
		if (m == in)
			die("No VLOG= found");

		m[-5] = 0;
		if (m[0] && m[1])
			strcpy(path, m);
		else
			strcpy(path, "/var/log/httpd");

		// Get current year and month
		time(&stamp);
		if (!strftime(date, sizeof(date), "%Y-%m", localtime(&stamp)))
			die("Date buffer overrun");

		// Put it all together
		snprintf(filename, sizeof(filename), "%s/VLOG-%s-%s.log",
			 path, date, vhost);

		// Check that it is not a symlink
		{
			struct stat s;
			lstat(filename, &s);
			if (S_ISLNK(s.st_mode))
				die("File is a symlink, dying!");
		}

		// Open destination file and write the log line
		i = open(filename, O_WRONLY|O_CREAT|O_APPEND, 0600);
		if (i == -1)
			die("Could not open file");

		strcat(in, "\n");
		write(i, in, strlen(in));
		close(i);
	}

	return 0;
}

