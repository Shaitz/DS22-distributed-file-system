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
//#define EVENT_SIZE  (3*sizeof(uint32_t)+sizeof(int))
#define EVENT_BUF_LEN     ( 1024 * ( EVENT_SIZE + 16 ) )
#define TESTIGO_NAME "inotify.example.executing"

int main(int argc, char *argv[])
{
  int length, i = 0;
  int fd;
  int wd;
  int wd_cd;
  char buffer[EVENT_BUF_LEN];
  char testigo[1024];
  char evento[1024];

  if (argc!=2) {
      fprintf(stderr, "Uso: %s Directorio_a_monitorizar\n", argv[0]);
      exit(1);
  }

//  fprintf(stderr, "---Prueba de inotify sobre %s\n", argv[1]);
//  fprintf(stderr, "---Notifica crear/borrar ficheros/directorios sobre %s\n", argv[1]);
//  fprintf(stderr, "---%s debe exixtir!\n", argv[1]);



  /*creating the INOTIFY instance*/
  fd = inotify_init();

  /*checking for error*/
  if ( fd < 0 ) {
    perror( "inotify_init" );
  }

  /*adding the /tmp directory into watch list. Here, the suggestion is to validate the existence of the directory before adding into monitoring list.*/
//  wd = inotify_add_watch( fd, "/tmp", IN_CREATE | IN_DELETE );

  /* Monitorizamos el directorio indicado como argumento. Debe estar creado. */
//  mkdir(argv[1]);
  wd_cd = inotify_add_watch( fd, argv[1], IN_CREATE | IN_DELETE | IN_MODIFY | IN_MOVE );

  /* Testigo para finalizar cuando lo borremos: */
  
  strcpy(testigo, argv[1]);
  strcat(testigo, "/");
  strcat(testigo, TESTIGO_NAME);
  mkdir(testigo);
  fprintf(stderr, "---Para salir, borrar %s/%s\n", argv[1], testigo); 


  /*read to determine the event change happens on the directory. Actually this read blocks until the change event occurs*/ 
  struct inotify_event event_st, *event;
  int k=0;
  int exiting= 0;

// printf("%s\n", argv[2]);
// printf("%s\n", argv[3]);
  write(1, "1\n", 2);

  while (!exiting) {
    fprintf(stderr, "---%s: waiting for event %d...\n", argv[0], ++k); 
    length = read( fd, buffer, EVENT_BUF_LEN ); 
    fprintf(stderr, "---%s: event %d read.\n", argv[0], k); 
    /*checking for error*/
    if ( length < 0 ) {
      perror( "read" );
      break;
    }
//    struct inotify_event *event = ( struct inotify_event * ) &buffer[ i ];
    while ( (i < length) && !exiting ) {
//    event= &event_st;
      event = ( struct inotify_event * ) &buffer[ i ];
//    fprintf(stderr, "---example: event name length: %i\n", event->len);
//    memcpy(event, buffer, length);
      if ( event->len ) {
//      memcpy(event+EVENT_SIZE, buffer+EVENT_SIZE, length);
        if ( event->mask & IN_CREATE ) {
          if ( event->mask & IN_ISDIR ) {	// event: directory created
            fprintf(stderr, "---%s: New directory %s created.\n", argv[0], event->name );
          }
          else {	// event: fie created
            fprintf(stderr, "---%s: New file %s created.\n", argv[0], event->name );
            sprintf(evento, "3\n%s\n", event->name );
            write(1, evento, strlen(evento));
//            printf("3\n%s\n", event->name );
          }
        }
        else if ( event->mask & IN_DELETE ) {
          if ( event->mask & IN_ISDIR ) {	// event: directory removed
            if (!strcmp(event->name, TESTIGO_NAME)) {
              exiting= 1;
//              break;
            }
            fprintf( stderr, "---%s: Directory %s deleted.\n", argv[0], event->name );
          }
          else {	// event: file removed
            fprintf(stderr, "---%s: File %s deleted.\n", argv[0], event->name );
            sprintf(evento, "4\n%s\n", event->name );
            write(1, evento, strlen(evento));
//            printf("4\n%s\n", event->name );
          }
        }
        else if (event->mask & IN_MODIFY) {
            fprintf(stderr, "---%s: File %s modified.\n", argv[0], event->name );
            sprintf(evento, "5\n%s\n", event->name );
            write(1, evento, strlen(evento));
        }
        else if (event->mask & IN_MOVE)
        {
          fprintf(stderr, "---%s: File %s moved to.\n", argv[0], event->name );
          sprintf(evento, "6\n%s\n", event->name );
          write(1, evento, strlen(evento));
        }
      }
      else {	// event ignored
        fprintf(stderr, "---%s: event ignored for %s\n", argv[0], event->name); 
      }
      i += EVENT_SIZE + event->len;
//    fprintf(stderr, "---example.event count: %i\n", i); 
    }
    i= 0;
  }

  fprintf(stderr, "---Exiting %s\n", argv[0]);
  write(1, "5\n", 2);
//  printf("5\n"); 
 /*removing the directory from the watch list.*/
  inotify_rm_watch( fd, wd );
  inotify_rm_watch( fd, wd_cd );
//  rmdir(argv[1]);

 /*closing the INOTIFY instance*/
  close( fd );

}
