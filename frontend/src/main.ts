import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { provideAnimations } from '@angular/platform-browser/animations';
import { AppComponent } from './app/app.component';
import player from 'lottie-web';
import { provideLottieOptions } from 'ngx-lottie';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

export function playerFactory() {
  return player;
}

const updatedConfig = {
  ...appConfig,
  providers: [
    ...(appConfig.providers || []),
    provideAnimations(),
    provideLottieOptions({
      player: playerFactory
    }), provideAnimationsAsync(),

  ]
};

bootstrapApplication(AppComponent, updatedConfig)
  .catch((err) => console.error(err));