#include <stdio.h>
#include <omp.h>
#include <assert.h>

int main() {
  fapp_start("foo",1,0);
  #pragma omp parallel
  {
    int num_threads = omp_get_num_threads();
    int tid = omp_get_thread_num();
    printf("thread %d/%d", tid, num_threads);
  }
  fapp_stop("foo",1,0);
  printf("\n");
  return 0;
}
