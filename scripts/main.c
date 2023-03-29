#include <stdio.h>
#include <omp.h>
#include <assert.h>

int main() {
  printf("Hello\n");
  #pragma omp parallel
  {
    int num_threads = omp_get_num_threads();
    int tid = omp_get_thread_num();
    printf("thread %d/%d\n", tid, num_threads);
  }
  return 0;
}
