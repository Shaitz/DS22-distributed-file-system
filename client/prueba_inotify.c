// Prueba de captura de notificaciones de Linux
// Adaptado de http://www.thegeekstuff.com/2010/04/inotify-c-program-example/
// por Alberto Lafuente, Fac. Informática UPV/EHU

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <linux/inotify.h>

#define EVENT_SIZE  ( sizeof (struct inotify_event) )
#define EVENT_BUF_LEN     ( 1024 * ( EVENT_SIZE + 16 ) )

int main(int argc, char *argv[])
{
  int length, i = 0;
  int fd;
  int wd;
  int wd_cd;
  char buffer[EVENT_BUF_LEN];
  char evento[1024];

  if (argc!=2) 
  {
      fprintf(stderr, "Uso: %s Directorio_a_monitorizar\n", argv[0]);
      exit(1);
  }

  fd = inotify_init();

  if ( fd < 0 )
    perror( "inotify_init" );

  char command[] = "python3 cli_fich.py";
  FILE* fp = popen(command, "w");

  if (fp == NULL)
  {
      exit(1);
  }

  wd_cd = inotify_add_watch( fd, argv[1], IN_CREATE | IN_DELETE | IN_MODIFY | IN_MOVE | IN_ATTRIB );

  /*read to determine the event change happens on the directory. Actually this read blocks until the change event occurs*/ 
  struct inotify_event event_st, *event;
  int k=0;
  int exiting= 0;

  while (!exiting) 
  {
    length = read( fd, buffer, EVENT_BUF_LEN ); 

    if ( length < 0 ) 
    {
      perror( "read" );
      break;
    }

    while ( (i < length) && !exiting ) 
    {
      event = ( struct inotify_event * ) &buffer[ i ];
      if ( event->len ) 
      {
        if ( event->mask & IN_CREATE ) 
        {
          if ( event->mask & IN_ISDIR ) // event: directory created
          {
            fprintf(fp, "DIR_CREATED %s\n", event->name);
            fflush(fp);
          }
          else 
          {	// event: fie created
            fprintf(fp, "FILE_CREATED %s\n", event->name);
            fflush(fp);
          }
        }
        else if ( event->mask & IN_DELETE ) 
        {
          if ( event->mask & IN_ISDIR ) 
          {	// event: directory removed
            fprintf(fp, "DIR_DELETED %s\n", event->name);
            fflush(fp);
          }
          else 
          {	// event: file removed
            fprintf(fp, "FILE_DELETED %s\n", event->name);
            fflush(fp);
          }
        }
        else if (event->mask & IN_MODIFY) 
        {	// event: file modified
            fprintf(fp, "FILE_MODIFIED %s\n", event->name);
            fflush(fp);
        }
        else if (event->mask & IN_MOVED_FROM)
        {
          fprintf(fp, "FILE_MOVED_FROM %s\n", event->name);
          fflush(fp);
        }
        else if (event->mask & IN_MOVED_TO)
        {
          fprintf(fp, "FILE_MOVED_TO %s\n", event->name);
          fflush(fp);
        }
        else if (event->mask & IN_ATTRIB)
        {
          fprintf(fp, "FILE_ATTRIB_CHANGED %s\n", event->name);
          fflush(fp);
        }
      }
      i += EVENT_SIZE + event->len;
    }
    i= 0;
  }

 /*removing the directory from the watch list.*/
  inotify_rm_watch( fd, wd_cd );

  pclose(fp);
  close( fd );

  return (0);

}
