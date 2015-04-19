#include <time.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <locale.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <pwd.h>
#include <grp.h>
#include <dirent.h>
#include <limits.h>
struct passwd *pws;
struct group *grp;
struct dirent *pak;
struct stat fileinfo;
FILE *plik=NULL, *p;
DIR *kat;
char tab[10240];
char czas_s[50];
time_t t;
struct tm *czas;
unsigned long rozmiar, mtime;
int x, i, ind1, ind2, v1, v2, mode, vmarker;
char *ver1[10], *ver2[10], *tmp, *tmp2, *tmp3, *e1, *e2, *hbsdir, *filetype, **except, *owner, *group, *mode_s, mode2_s[10], *filename, vstring[10];

void print_help(int status) {
printf("HBS Helper - helper binary for the Hierophant Build System.\n");

printf("--time [seconds_since_Epoch [strftime-format-string]]\n\
\t(shows current/translates given Epoch time)\n\
--dirs-show\n\
\t(scans stdin, prints lines with trailing slashes)\n\
--dirs-hide\n\
\t(scans stdin, prints lines without trailing slashes)\n\
--size number_of_bytes\n\
\t(takes a number and reformats it to KB/MB notation)\n\
--fast-tar\n\
\t(outputs a \"--occurrence=1\" string if local \"tar\" supports it\n\
--check-uid\n\
\t(exits with error code == 1 if user is not root)\n\
--get-files hbs_dir filename [omit_dir1 omit_dir2 ...]\n\
\t(scans all subdirs in hbs_dir, returning paths to files matching\n\
\t\"filename\", except for those in omit_dir1, omit_dir2 etc.)\n\
--grep-files hbs_dir filename string [string2 ...]\n\
\t(scans all \"filenames\" in hbs_dir for occurences of \"string\",\n\
\tprints package name if matched, automatically ignores extra fields\n\
\tif \"filename\" == \"FILELIST\")\n\
--get-pkgdirs hbs_dir [omit_dir1 omit_dir2 ...]\n\
\t(scans directory hbs_dir looking for subdirectories,\n\
\texcepts those matching omit_dir1, omit_dir2 etc.)\n\
--cut-filelists [filelist1 filelist2 filelist3 ...]\n\
\t(parses filelists, strips mode, username and group\n\
\tfields, printing only filenames)\n\
--print-lines x-y [file1 file2 ...]\n\
\t(takes files file1, file2 [...] and prints lines\n\
\tin range x-y, eg. lines 3-5)\n\
--verify-packages [pkg1 pkg2 ...]\n\
\t(Checks files from pkg1, pkg2 (...) and prints filenames\n\
\tof modified files)\n\
--terminal\n\
\t(Exits with code 0 if output is directed to a TTY device,\n\
\treturns with code 1 otherwise)\n\
--realpath [path1 path2 ...]\n\
\t(returns canonicalized absolute versions of given pathnames)\n\
--rm-from-list list_file\n\
\t(removes files listed in list_file)\n\
--rmdir-from-list list_file\n\
\t(removes directories listed in list_file)\n");
exit(status);
}

int main(int argc, char *argv[]) {
	if (argc <= 1) {
		print_help(0);
	}
	setlocale(LC_TIME,"");

	if (strcmp(argv[1],"--time")==0) {
		if (argc > 2) {
				t=atoi(argv[2]);
				czas=localtime(&t);
				if (argc == 4) {
				strftime(czas_s,sizeof(czas_s),argv[3],czas);
				} else {
				strftime(czas_s,sizeof(czas_s),"%Y%m%d %T, %A",czas);
				}
				printf("%s\n",czas_s);
		} else {
			printf("%i\n",(int)time(NULL));
		}
	} 
	else if (strcmp(argv[1],"--dirs-show")==0) {
		while (fgets(tab, sizeof(tab), stdin)) {
			if (tab[strlen(tab)-2]=='/') {
			printf(tab);
			}
		}
	}
	else if (strcmp(argv[1],"--dirs-hide")==0) {
		while (fgets(tab, sizeof(tab), stdin)) {
			if (tab[strlen(tab)-2]!='/') {
			printf(tab);
			}
		}
	}
	else if (strcmp(argv[1],"--terminal")==0) {
		if (isatty(1)) {
			exit(0);
		} else {
			exit(1);
		}
	}
	else if (strcmp(argv[1],"--size")==0) {
		rozmiar=atol(argv[2]);
		if (rozmiar < 1024*1024) {
				if ((float)rozmiar/1024-rozmiar/1024!=0) {
				printf("%.2fKB\n",(float)rozmiar/1024);
				} else {
				printf("%liKB\n",rozmiar/1024);
				}
		} else {
				if ((float)rozmiar/1024/1024-rozmiar/1024/1024!=0) {
				printf("%.2fMB\n",(float)rozmiar/1024/1024);
				} else {
				printf("%liMB\n",rozmiar/1024/1024);
				}
		}
	}		
	else if (strcmp(argv[1],"--fast-tar")==0) {
		system("tar --help > /tmp/.hbs_helper");
		plik=fopen("/tmp/.hbs_helper","r");
		while (fgets(tab,sizeof(tab),plik)) {
				if (strstr(tab,"--occurrence")!=NULL) {
				printf("--occurrence=1\n");
				}
		}
		unlink("/tmp/.hbs_helper");
	}
	else if (strcmp(argv[1],"--check-uid")==0) {
		pws = getpwuid(geteuid());
		if (strcmp(pws->pw_name,"root")!=0) {
				exit(1);
		} else {
				exit(0);
		}
	}
	else if (strcmp(argv[1],"--get-files")==0) {
		hbsdir=argv[2];
		filetype=argv[3];
		x=argc-3;
		if (x>0) {
			except=calloc(x,sizeof(char *));
			for (i=4;i<argc;i++) {
					except[i-4]=argv[i];
			}
		}
		kat=opendir(hbsdir);
		while ((pak=readdir(kat))) {
				if (pak->d_name[0]=='.') {
						continue;
				}
				strcpy(tab,hbsdir);
				strcat(tab,"/");
				strcat(tab,pak->d_name);
				for (i=4;i<argc;i++) {
						if (strcmp(tab,except[i-4])==0) {
								i=-1;
								break;
						}
				}
				if (i==-1) { continue; }
				stat(tab,&fileinfo);
			if (!S_ISDIR(fileinfo.st_mode)) { continue; }
				strcat(tab,"/");
				strcat(tab,filetype);
				if (stat(tab,&fileinfo)==-1) { continue; }
				printf("%s\n",tab);
		}
		closedir(kat);
		free(except);
	}
//sep
	else if (strcmp(argv[1],"--grep-files")==0) {
		hbsdir=argv[2];
		filetype=argv[3];
		x=argc-3;
		if (x>0) {
			tmp3=calloc(argc,sizeof(char *));
			for (i=4;i<argc;i++) {
					filename=malloc(4096);
					lstat(argv[i], &fileinfo);
					if (!S_ISLNK(fileinfo.st_mode)) {
						argv[i]=realpath(argv[i],filename);
					} else {
					tmp=rindex(argv[i],'/');
					if (tmp!=NULL) {
						tmp[0]='\0';
						argv[i]=realpath(argv[i],filename);
						strcat(filename,"/");
						strcat(filename,tmp+1);
					} else {
						getcwd(filename,4095);
						strcat(filename,"/");
						strcat(filename,argv[i]);
					}
					}
					if (S_ISDIR(fileinfo.st_mode)) strcat(filename, "/");
					argv[i]=filename;
					e1=malloc(4096);
			}
		} else {
				fprintf(stderr,"Not enough arguments!\n");
				exit(1);
		}
		kat=opendir(hbsdir);
		while ((pak=readdir(kat))) {
				if (pak->d_name[0]=='.') {
						continue;
				}
				strcpy(tab,hbsdir);
				strcat(tab,"/");
				strcat(tab,pak->d_name);
				stat(tab,&fileinfo);
			if (!S_ISDIR(fileinfo.st_mode)) { continue; }
				tmp2=strrchr(tab,'/')+1;
				tmp=malloc(strlen(tmp2)+1);
				strcpy(tmp,tmp2);
				strcat(tab,"/");
				strcat(tab,filetype);
				if (stat(tab,&fileinfo)==-1) { continue; }
				//'tab' contains the filename to grep
				//'tmp' contains the package name
				//'filetype' contains the file type
				plik=fopen(tab,"r");
				strcpy(e1,tab);
				e2=strrchr(e1,'/');
				e2[1]='\0';
				strcat(e1,"INFO");
				p=fopen(e1,"r");
				fgets(e1,4096,p);
				fclose(p);
				while (fgets(tab, sizeof(tab), plik)) {
					if (!strcmp("FILELIST",filetype)) {
					tmp2=strchr(tab,':');
					tmp2=strchr(tmp2+1,':');
					tmp2=strchr(tmp2+1,':');
					strcpy(tab,tmp2+1);
					}
					tab[strlen(tab)-1]='\0';
					
					for (i=4;i<argc;i++) {
						if (!strcmp(tab,argv[i])) {
							printf("%s: %s",tab,e1);
							tmp3[i]=1;
						}
					}
				}
				fclose(plik);
		}
		closedir(kat);
		for (i=4;i<argc;i++) {
			if (tmp3[i]==0) fprintf(stderr,"%s: ???\n",argv[i]);
		}
	}
//sep
	else if (strcmp(argv[1],"--get-pkgdirs")==0) {
		hbsdir=argv[2];
		x=argc-2;
		if (x>0) {
			except=calloc(x,sizeof(char *));
			for (i=3;i<argc;i++) {
				except[i-3]=argv[i];
			}
		}
		kat=opendir(hbsdir);
		while ((pak=readdir(kat))) {
				if (pak->d_name[0]=='.') {
					continue;
				}
				strcpy(tab,hbsdir);
				strcat(tab,"/");
				strcat(tab,pak->d_name);
				for (i=3;i<argc;i++) {
					if (strcmp(tab,except[i-3])==0) {
						i=-1;
						break;
					}
				}
				if (i==-1) { continue; }
				stat(tab,&fileinfo);
			if (!S_ISDIR(fileinfo.st_mode)) { continue; }
				printf("%s\n",tab);
		}
		closedir(kat);
		free(except);
	} else if (strcmp(argv[1],"--cut-filelists")==0) {
		for (i=2;i<argc;i++) {
			plik=fopen(argv[i],"r");
			while (fgets(tab, sizeof(tab), plik)) {
				tmp=strchr(tab,':');
				tmp=strchr(tmp+1,':');
				tmp=strchr(tmp+1,':');
				printf(tmp+1);
			}
			fclose(plik);
		}

	} else if (strcmp(argv[1],"--rm-from-list")==0) {
		plik=fopen(argv[2],"r");
		while (fgets(tab, sizeof(tab), plik)) {
			rozmiar=strlen(tab);
			if (tab[rozmiar-1]=='\n') tab[rozmiar-1]='\0';
			if (unlink(tab)) printf("Couldn't remove %s\n",tab);
		}
		fclose(plik);
	} else if (strcmp(argv[1],"--rmdir-from-list")==0) {
		plik=fopen(argv[2],"r");
		while (fgets(tab, sizeof(tab), plik)) {
			rozmiar=strlen(tab);
			if (tab[rozmiar-1]=='\n') tab[rozmiar-1]='\0';
			if (rmdir(tab)) printf("Couldn't remove %s\n",tab);
		}
		fclose(plik);
	} else if (strcmp(argv[1],"--print-lines")==0) {
			tmp=strchr(argv[2],'-');
			*tmp='\0';
			ind1=strtol(argv[2],NULL,10)-1;
			ind2=strtol(++tmp,NULL,10)-1;
			*tmp='-';
			for (x=3;x<argc;x++) {
				plik=fopen(argv[x],"r");
				for (i=0;i<=ind2;i++) {
					fgets(tab, sizeof(tab), plik);
					if (i>=ind1) {printf(tab); }
				}
				fclose(plik);
			}
	} else if (strcmp(argv[1],"--verify-packages")==0) {
			for (x=2;x<argc;x++) {
				e2=strrchr(argv[x],'/')+1;
				//printf("VERIFY: %s\n",e2);
				v1=strlen(argv[x])+25;
				tmp=malloc(v1);
				e1=malloc(v1);
				strcpy(tmp,argv[x]);
				strcpy(e1,argv[x]);
				strcat(tmp,"/FILELIST");
				strcat(e1,"/INFO");
				plik=fopen(e1,"r");
				if (plik==NULL) { printf("Couldn't open %s\n", e1); continue; }
				while (fgets(tab, sizeof(tab), plik));
				fclose(plik);
				mtime=strtol(tab,NULL,10);
				plik=fopen(tmp,"r");
				if (plik==NULL) { printf("Couldn't open %s\n", tmp); continue; }
				while (fgets(tab, sizeof(tab), plik)) {
				tab[strlen(tab)-1]='\0';
				tmp2=strchr(tab,':');
				*tmp2='\0';
				mode_s=tab;
				owner=tmp2+1;
				tmp2=strchr(tmp2+1,':');
				*tmp2='\0';
				group=tmp2+1;
				filename=strchr(tmp2+1,':');
				*filename='\0';
				filename++;
				strcpy(vstring,"....");
				vmarker=0;
				if (lstat(filename,&fileinfo)==-1) { 
				strcpy(vstring,"miss");
				vmarker=1;
				} else {
				sprintf(mode2_s,"%o",fileinfo.st_mode);
				tmp2=mode2_s+strlen(mode2_s)-4;
				pws=getpwuid(fileinfo.st_uid);
				grp=getgrgid(fileinfo.st_gid);
				if (strcmp(pws->pw_name,owner)!=0) { vstring[1]='O'; vmarker=1; }
				if (strcmp(grp->gr_name,group)!=0) { vstring[2]='G'; vmarker=1; }
				if (strcmp(tmp2,mode_s)!=0 && !S_ISLNK(fileinfo.st_mode)) { vstring[0]='M'; vmarker=1; }
				if ((fileinfo.st_mtime>mtime) && !S_ISDIR(fileinfo.st_mode)) { vstring[3]='T'; vmarker=1; }
				}
				if (vmarker) { printf("%s\t%s\n",vstring,filename); }
				}
				fclose(plik);
			free(tmp);
			free(e1);
			}
	} else if (strcmp(argv[1],"--realpath")==0) {
		filename=malloc(PATH_MAX+1);
		for (x=2;x<argc;x++) {
			realpath(argv[x],filename);
			lstat(filename, &fileinfo);
			if (S_ISDIR(fileinfo.st_mode)) strcat(filename, "/");
			printf("%s\n",filename);
		}
		free(filename);
	} else {
		print_help(2);
	}
	return 0;
}
